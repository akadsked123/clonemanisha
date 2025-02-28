from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from apps.timetable.models import InitialSchedulerData
from apps.user.models import User
from apps.algorithm.data import Data
from apps.algorithm.ga import GeneticAlgorithm
from apps.user.common.user_notification import create_notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

css_content = '''
        body {
          font-family: Helvetica, sans-serif;
          -webkit-font-smoothing: antialiased;
          font-size: 16px;
          line-height: 1.3;
          -ms-text-size-adjust: 100%;
          -webkit-text-size-adjust: 100%;
        }
        table {
          border-collapse: separate;
          mso-table-lspace: 0pt;
          mso-table-rspace: 0pt;
          width: 100%;
        }
        table td {
          font-family: Helvetica, sans-serif;
          font-size: 16px;
          vertical-align: top;
        }
        body {
          background-color: #f4f5f6;
          margin: 0;
          padding: 0;
        }
        .body {
          background-color: #f4f5f6;
          width: 100%;
        }
        .container {
          margin: 0 auto !important;
          max-width: 600px;
          padding: 0;
          padding-top: 24px;
          width: 600px;
        }
        .content {
          box-sizing: border-box;
          display: block;
          margin: 0 auto;
          max-width: 600px;
          padding: 0;
        }
        .main {
          background: #ffffff;
          border: 1px solid #eaebed;
          border-radius: 16px;
          width: 100%;
        }
        .wrapper {
          box-sizing: border-box;
          padding: 24px;
        }
        .footer {
          clear: both;
          padding-top: 24px;
          text-align: center;
          width: 100%;
        }
        .footer td,
        .footer p,
        .footer span,
        .footer a {
          color: #9a9ea6;
          font-size: 16px;
          text-align: center;
        }
        p {
          font-family: Helvetica, sans-serif;
          font-size: 16px;
          font-weight: normal;
          margin: 0;
          margin-bottom: 16px;
        }
        a {
          color: #059669;
          text-decoration: underline;
        }
        .btn {
          box-sizing: border-box;
          min-width: 100% !important;
          width: 100%;
        }
        .btn > tbody > tr > td {
          padding-bottom: 16px;
        }
        .btn table {
          width: auto;
        }
        .btn table td {
          background-color: #ffffff;
          border-radius: 4px;
          text-align: center;
        }
        .btn a {
          background-color: #ffffff;
          border: solid 2px #059669;
          border-radius: 4px;
          box-sizing: border-box;
          color: #059669;
          cursor: pointer;
          display: inline-block;
          font-size: 16px;
          font-weight: bold;
          margin: 0;
          padding: 12px 24px;
          text-decoration: none;
          text-transform: capitalize;
        }
        .btn-primary table td {
          background-color: #059669;
        }
        .btn-primary a {
          background-color: #059669;
          border-color: #059669;
          color: #ffffff;
        }
        @media all {
          .btn-primary table td:hover {
            background-color: #047857 !important;
          }
          .btn-primary a:hover {
            background-color: #047857 !important;
            border-color: #047857 !important;
          }
        }
        @media only screen and (max-width: 640px) {
          .main p,
          .main td,
          .main span {
            font-size: 16px !important;
          }
          .wrapper {
            padding: 8px !important;
          }
          .content {
            padding: 0 !important;
          }
          .container {
            padding: 0 !important;
            padding-top: 8px !important;
            width: 100% !important;
          }
          .main {
            border-left-width: 0 !important;
            border-radius: 0 !important;
            border-right-width: 0 !important;
          }
          .btn table {
            max-width: 100% !important;
            width: 100% !important;
          }
          .btn a {
            font-size: 16px !important;
            max-width: 100% !important;
            width: 100% !important;
          }
        }
        @media all {
          .ExternalClass {
            width: 100%;
          }
          .ExternalClass,
          .ExternalClass p,
          .ExternalClass span,
          .ExternalClass font,
          .ExternalClass td,
          .ExternalClass div {
            line-height: 100%;
          }
          .apple-link a {
            color: inherit !important;
            font-family: inherit !important;
            font-size: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
            text-decoration: none !important;
          }
          #MessageViewBody a {
            color: inherit;
            text-decoration: none;
            font-size: inherit;
            font-family: inherit;
            font-weight: inherit;
            line-height: inherit;
          }
        }
        '''
@shared_task
def run_genetic_algorithm(merged_file_path, user_info_list, initial_scheduler_data_ids):
    try:
        data = Data.load_data(merged_file_path)
        user_ids = [user_info[1] for user_info in user_info_list]
        genetic_algorithm = GeneticAlgorithm()
        result = genetic_algorithm.run(data, user_ids, initial_scheduler_data_ids)
        InitialSchedulerData.objects.filter(scheduler_id__in=initial_scheduler_data_ids).update(status=4)

        channel_layer = get_channel_layer()
        for user_email, user_id, username, full_name in user_info_list:
            async_to_sync(channel_layer.group_send)(
                  f"{user_id}",
                  {
                      "type": "send_notification",
                      "message": "The schedule generation process has completed successfully. Please reload the page."
                  }
              )
            subject = 'Schedule Generation Completed - Adjustments Needed'
            html_content = f'''
            <!doctype html>
            <html lang="en">
              <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <title>Schedule Notification</title>
                <style>
                {css_content}
                </style>
              </head>
              <body>
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
                  <tr>
                    <td>&nbsp;</td>
                    <td class="container">
                      <div class="content">
                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="main">
                          <tr>
                            <td class="wrapper">
                            <p style="text-transform: capitalize;">Hello, {full_name}</p>
                              <p>The schedule generation process has completed successfully. Please review the generated schedule and make any necessary adjustments.</p>
                              <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="btn btn-primary">
                                <tbody>
                                  <tr>
                                    <td align="left">
                                      <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                        <tbody>
                                          <tr>
                                            <td> <a href="#" target="_blank">Review Schedule</a> </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </td>
                                  </tr>
                                </tbody>
                              </table>
                              <p>Best Regards,<br>AcadSked Team</p>
                            </td>
                          </tr>
                          </table>
                        <div class="footer">
                          <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                            <tr>
                              <td class="content-block">
                                <span class="apple-link">All Rights Reserved 2024</span>
                              </td>
                            </tr>
                          </table>
                         
                        </div>
                         <br>
                          <br>
                      </div>
                    </td>
                    <td>&nbsp;</td>
                  </tr>
                </table>
              </body>
            </html>
            '''
            
            email = EmailMultiAlternatives(subject, '',settings.DEFAULT_FROM_EMAIL, [user_email])
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            user = User.objects.get(id=user_id)
            create_notification(
                recipient=user,
                message="The schedule generation process has completed successfully. Please review the generated schedule and make any necessary adjustments.",
                status=1,
                sender=user,
                notification_url=f'/user/notification/{username}'
            )
        
        return result 
    except Exception as e:
        for user_email, user_id, username, full_name in user_info_list:
            subject = 'Schedule Generation Failed'
            html_content = f'''
            <!doctype html>
            <html lang="en">
              <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <title>Schedule Notification</title>
                <style>
                {css_content}
                </style>
              </head>
              <body>
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
                  <tr>
                    <td>&nbsp;</td>
                    <td class="container">
                      <div class="content">
                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="main">
                          <tr>
                            <td class="wrapper">
                              <p>Hello, {full_name}!</p>
                              <p>We encountered an issue while generating your requested schedule. We apologize for the inconvenience. Please try submitting your request again. If the error persists, kindly report it to our support team for further assistance.</p>
                              <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="btn btn-primary">
                                <tbody>
                                  <tr>
                                    <td align="left">
                                      <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                        <tbody>
                                          <tr>
                                            <td> <a href="http://yourwebsite.com/support" target="_blank">Contact Support</a> </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </td>
                                  </tr>
                                </tbody>
                              </table>
                              <p>Best Regards,<br>AcadSked Team</p>
                            </td>
                          </tr>
                          </table>
                        <div class="footer">
                          <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                            <tr>
                              <td class="content-block">
                                 <span class="apple-link">All Rights Reserved 2024</span>
                              </td>
                            </tr>
                          </table>
                        
                        </div>
                           <br>
                          <br>
                      </div>
                    </td>
                    <td>&nbsp;</td>
                  </tr>
                </table>
              </body>
            </html>
            '''
            email = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [user_email])
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            InitialSchedulerData.objects.filter(scheduler_id__in=initial_scheduler_data_ids).update(status=5)

            user = User.objects.get(id=user_id)
            create_notification(
                recipient=user,
                message="There was an issue generating your schedule. Please try again, or contact support if the problem persists.",
                status=1,
                sender=user,
                notification_url=f'/user/notification/{username}'
            )
        return f"Error running Genetic Algorithm: {str(e)}"