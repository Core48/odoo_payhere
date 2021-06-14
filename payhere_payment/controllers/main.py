# -*- coding: utf-8 -*-
#
#    Copyright (C) 2021 Core48 - https://core48.com/
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class PayhereController(http.Controller):

    @http.route(['/payment/payhere/response'], type='http', auth='public', csrf=False)
    def payhere_response(self, **post):
        _logger.info('PayHere: entering feedback with post response data %s', pprint.pformat(post))
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'payhere')
        return werkzeug.utils.redirect('/payment/process')

    @http.route(['/payment/payhere/return', '/payment/payhere/cancel'], type='http', auth='public', csrf=False)
    def payhere_return(self, **post):
        _logger.info('PayHere: entering feedback with post response data %s', pprint.pformat(post))

        return werkzeug.utils.redirect('/payment/process')