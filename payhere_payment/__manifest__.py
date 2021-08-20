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
{
    'name': "Payhere Payment Acquirer",
    'summary': """
        Payment Acquirer: PayHere Implementation
        """,
    'description': """
        PayHere payment gateway integration for Odoo
    """,
    'author': "Core48",
    'company': 'Core48',
    'website': "https://core48.com",
    'maintainer': 'Core48',
    'category': 'Payment',
    'license':'LGPL-3',
    'version': '13.0.1.0.0',
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_payhere_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://www.youtube.com/watch?v=keV39Xy-O34',
    'images': ['static/description/banner.jpg'],
}
