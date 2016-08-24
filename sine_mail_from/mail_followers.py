from email.utils import formataddr
from openerp.osv import osv, fields
from openerp import tools, SUPERUSER_ID


class mail_notification(osv.Model):
    _inherit = 'mail.notification'

    def _notify(self, cr, uid, msg_id, partners_to_notify=None, context=None):
        """ Send by email the notification depending on the user preferences

            :param list partners_to_notify: optional list of partner ids restricting
                the notifications to process
        """
        if context is None:
            context = {}
        mail_message_obj = self.pool.get('mail.message')

        # optional list of partners to notify: subscribe them if not already done or update the notification
        if partners_to_notify:
            notifications_to_update = []
            notified_partners = []
            notif_ids = self.search(cr, SUPERUSER_ID,
                                    [('message_id', '=', msg_id), ('partner_id', 'in', partners_to_notify)],
                                    context=context)
            for notification in self.browse(cr, SUPERUSER_ID, notif_ids, context=context):
                notified_partners.append(notification.partner_id.id)
                notifications_to_update.append(notification.id)
            partners_to_notify = filter(lambda item: item not in notified_partners, partners_to_notify)
            if notifications_to_update:
                self.write(cr, SUPERUSER_ID, notifications_to_update, {'read': False}, context=context)
            mail_message_obj.write(cr, uid, msg_id, {'notified_partner_ids': [(4, id) for id in partners_to_notify]},
                                   context=context)

        # mail_notify_noemail (do not send email) or no partner_ids: do not send, return
        if context.get('mail_notify_noemail'):
            return True
        # browse as SUPERUSER_ID because of access to res_partner not necessarily allowed
        msg = self.pool.get('mail.message').browse(cr, SUPERUSER_ID, msg_id, context=context)
        notify_partner_ids = self.get_partners_to_notify(cr, uid, msg, partners_to_notify=partners_to_notify,
                                                         context=context)
        if not notify_partner_ids:
            return True

        # add the context in the email
        # TDE FIXME: commented, to be improved in a future branch
        # quote_context = self.pool.get('mail.message').message_quote_context(cr, uid, msg_id, context=context)

        mail_mail = self.pool.get('mail.mail')
        # add signature
        body_html = msg.body
        # if quote_context:
        # body_html = tools.append_content_to_html(body_html, quote_context, plaintext=False)
        signature = msg.author_id and msg.author_id.user_ids and msg.author_id.user_ids[0].signature or ''
        if signature:
            body_html = tools.append_content_to_html(body_html, signature, plaintext=True, container_tag='div')

        # email_from: partner-user alias or partner email or mail.message email_from
        if msg.author_id.email:
            email_from = msg.author_id.email
        elif msg.author_id and msg.author_id.user_ids and msg.author_id.user_ids[0].alias_domain and \
                msg.author_id.user_ids[0].alias_name:
            email_from = formataddr((msg.author_id.name, '%s@%s' % (
                msg.author_id.user_ids[0].alias_name, msg.author_id.user_ids[0].alias_domain)))
        elif msg.author_id:
            email_from = formataddr((msg.author_id.name, msg.author_id.email))
        else:
            email_from = msg.email_from

        references = False
        if msg.parent_id:
            references = msg.parent_id.message_id

        mail_values = {
            'mail_message_id': msg.id,
            'auto_delete': True,
            'body_html': body_html,
            'email_from': email_from,
            'references': references,
        }
        if 'mail_server_id' in context:
            # temporary workaround for mail from send mail wizard
            mail_values['mail_server_id'] = context['mail_server_id']
        email_notif_id = mail_mail.create(cr, uid, mail_values, context=context)
        try:
            return mail_mail.send(cr, uid, [email_notif_id], recipient_ids=notify_partner_ids, context=context)
        except Exception:
            return False
