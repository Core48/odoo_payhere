# -*- coding: utf-8 -*-
#
#    Copyright (C) 2021 Core48 - https://core48.com/
#    This program is free software: you can modify
#    it under the terms of the GNU Lesser General Public License (LGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import uuid

from hashlib import md5
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError


_logger = logging.getLogger(__name__)


class PaymentAcquirerPayhere(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('payhere', 'PayHere')])
    payhere_merchant_id = fields.Char(string="PayHere Merchant ID", required_if_provider='payhere', groups='base.group_user')
    payhere_merchant_secret = fields.Char(string="PayHere Merchant Secret", required_if_provider='payhere', groups='base.group_user')

    def _get_payhere_urls(self, environment):
        if environment == 'prod':
            return 'https://www.payhere.lk/pay/checkout'
        return 'https://sandbox.payhere.lk/pay/checkout'


    def _payhere_generate_sign(self, inout, values):
        if inout not in ('in', 'out'):
            raise Exception("Type must be 'in' or 'out'....")
        merchant_secret_md5 = (md5((self.payhere_merchant_secret).encode('utf-8')).hexdigest()).upper()
        if inout == 'in':
            data_to_hash = (self.payhere_merchant_id + values['order_id'] +
                            str(values['amount']) + values['currency'] + merchant_secret_md5)
        else:
            data_to_hash = (self.payhere_merchant_id + values['order_id'] +
                            str(values['payhere_amount']) + values['payhere_currency'] + 
                            values['status_code']+ merchant_secret_md5)
        
        return (md5(data_to_hash.encode('utf-8')).hexdigest()).upper()
    

    def payhere_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        tx = self.env['payment.transaction'].search([('reference', '=', values.get('reference'))])
        tx_so_id = self.env['sale.order'].search([('transaction_ids', '=', values.get('reference'))])
        if tx.state not in ['done', 'pending']:
            tx.reference = str(uuid.uuid4())
        payhere_values = values

        
        
        payhere_values.update({
            "merchant_id": self.payhere_merchant_id,
            "return_url": urls.url_join(base_url, '/payment/payhere/return'),
            "cancel_url":urls.url_join(base_url, '/payment/payhere/cancel'),
            "notify_url":urls.url_join(base_url, '/payment/payhere/response'),
            "currency":values['currency'].name,
            "amount_total":values['amount'],
            "order_id":tx.reference,        

        })
        payhere_values['hash'] = self._payhere_generate_sign("in", payhere_values)
        return payhere_values
    

    def payhere_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_payhere_urls(environment)




class PaymentTransactionPayhere(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _payhere_form_get_tx_from_data(self, data):
        reference, md5sig = data.get('order_id'), data.get('md5sig')

        if not reference or not md5sig:
            error_msg=_('PayHere: received data with missing reference (%s) or md5sign (%s)') % (reference, md5sig)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        transaction = self.env['payment.transaction'].search([('reference', '=', reference)])

        if not transaction or len(transaction) > 1:
            error_msg = 'PayHere: received data for reference %s' % (reference)
            if not transaction:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        md5sign_check = transaction.acquirer_id._payhere_generate_sign('out', data)

        if md5sign_check.upper() != md5sig.upper():
            raise ValidationError(('Payhere: invalid Md5sign, received %s, computed %s, for data %s') % (md5sig, md5sign_check, data))
        return transaction[0]


    def _payhere_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if self.acquirer_reference and data.get('mmp_txn') != self.acquirer_reference:
            invalid_parameters.append (('order_id', data.get('order_id'), self.acquirer_reference))

        return invalid_parameters


    def _payhere_form_validate(self, data):
        status = data.get('status_code')
        result = self.write({
            'acquirer_reference':self.env['payment.acquirer'].search ([]),
            'date':fields.Datetime.now()
        })

        if status == '2':
            _logger.info('Validated PayHere payment for tx %s: set as done' % (self.reference))
            self._set_transaction_done()
        elif status == '-2':
            _logger.info('Validated PayHere payment for tx %s: status code :%s set as error' % (self.reference, status))
            self._set_transaction_error()
        elif status in ['-1','-3']:
            _logger.info('Validated PayHere payment for tx %s: status code :%s set as cancel' % (self.reference, status))
            self._set_transaction_cancel()
        else:
            _logger.info('Validated PayHere payment for tx %s: status code :%s set as pending' % (self.reference, status))
            self._set_transaction_pending()
        return result
