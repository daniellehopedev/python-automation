import requests
import smtplib
import os
import paramiko
import linode_api4
import time
import schedule

# env variables
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
LINODE_TOKEN = os.environ.get('LINODE_TOKEN')

def restart_server_and_container():
    # restart linode server
    print('Rebooting the server...')
    client = linode_api4.LinodeClient(LINODE_TOKEN)
    # connect to a resource on linode, '123' would be the ID of the linode server (Linode ID)
    nginx_server = client.load(linode_api4.Instance, 123)
    nginx_server.reboot()

    # restart the application
    while True:
        nginx_server = client.load(linode_api4.Instance, 123)
        if nginx_server.status == 'running':
            time.sleep(5)
            restart_container()
            break

def send_notification(email_msg):
    print('Sending an email...')
    # smtp email provider for gmail and the port
    with smtp.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls() # encrypt the communication from the python app to the email server
        smtp.ehlo() # ids the python app with the email server
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)   # login to your gmail account (create a application specific password instead of your own password)
        message = f"Subject: SITE DOWN\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

def restart_container():
    print('Restarting the application...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='<cloud_server_ip>', username='root', key_filename='<path_to_own_ssh_key_file>')
    stdin, stdout, stderr = ssh.exec_command('docker start <docker_container_id>')
    print(stdout.readlines())
    ssh.close()

def monitor_application():
    try:
        response = requests.get('<linode_server_url>')
        if response.status_code == 200:
            print('Application is running successfully!')
        else:
            print('Application Down. Fix it!')
            msg = f'Application returned {response.status_code}'
            send_notification(msg)
            restart_container()
    except Exception as ex:
        print(f'Connection error happened: {ex}')
        msg = 'Application not accessible at all'
        send_notification(msg)
        restart_server_and_container()

schedule.every(5).minutes.do(monitor_application)

while True:
    schedule.run_pending()