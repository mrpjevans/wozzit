from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import requests, json, logging, platform, sys, smtplib
import message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

if platform.system() == 'Darwin':
        import pync
if platform.system() == 'Windows':
    from win10toast import ToastNotifier # pylint: disable=all
if platform.system() == 'Linux':
    import notify2

# Our very simple HTTP server
class WozzitRequestHandler(BaseHTTPRequestHandler):
    
    parentSvr = None

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # Currently GET has no function, but must be implemented
    def do_GET(self):
        logging.info('GET received from %s', self.client_address[0])
        logging.info('Not found')
        msg = message.NotFoundMessage()
        self._set_headers()
        self.wfile.write(msg.toJSON())

    def do_HEAD(self):
        self._set_headers()

    # You send a message to the server using HTTP POST with a application/json content-type
    def do_POST(self):
        logging.info('POST received from %s', self.client_address[0])
        contentLength = int(self.headers['Content-Length'])
        rawData = self.rfile.read(contentLength)
        logging.debug(rawData)
        receipt = self.parentSvr.processActions(rawData, self.client_address[0])
        self._set_headers()
        self.wfile.write(receipt.toJSON())
    
    # PUT is not implemented
    def do_PUT(self):
        logging.info('PUT received from %s', self.client_address[0])
        logging.debug('Not implemented')
        msg = message,NotImplementedMessage()
        self._set_headers()
        self.wfile.write(msg.toJSON())

    # PATCH is not implemented
    def do_PATCH(self):
        logging.info('PATCH received from %s', self.client_address[0])
        logging.debug('Not implemented')
        msg = message.NotImplementedMessage()
        self._set_headers()
        self.wfile.write(msg.toJSON())

    # Delete is not implemented
    def do_DELETE(self):
        logging.debug('DELETE received from %s', self.client_address[0])
        logging.debug('Not implemented')
        msg = message.NotImplementedMessage()
        self._set_headers()
        self.wfile.write(msg.toJSON())

    def log_message(self, format, *args):
        logging.info("%s %s" % (self.client_address[0],format%args))

class Server:
    
    # Stack of event listeners
    actions = []

    # SMTP Settings for sending emails
    smtp = {
        "host": None,
        "port": None,
        "SSL": None,
        "username": None,
        "password": None,
        "fromName": None,
        "fromEmail": None
    }

    # Callback holder for errors
    onError =  None

    # Options, options, options
    def setOptions(self, opts={}):
        
        # Server Options
        self.port = opts['port'] if opts.has_key('port') else 10207
        self.ip = opts['ip'] if opts.has_key('ip') else ''

        # Email Options
        self.smtp['host'] = opts['smtp']['host'] if opts.has_key('smtp') and opts['smtp'].has_key('host') else None
        self.smtp['port'] = opts['smtp']['port'] if opts.has_key('smtp') and opts['smtp'].has_key('port') else 25
        self.smtp['SSL'] = opts['smtp']['SSL'] if opts.has_key('smtp') and opts['smtp'].has_key('SSL') else False
        self.smtp['username'] = opts['smtp']['username'] if opts.has_key('smtp') and opts['smtp'].has_key('username') else None
        self.smtp['password'] = opts['smtp']['password'] if opts.has_key('smtp') and opts['smtp'].has_key('password') else None
        self.smtp['fromName'] = opts['smtp']['fromName'] if opts.has_key('smtp') and opts['smtp'].has_key('fromName') else None
        self.smtp['fromEmail'] = opts['smtp']['fromEmail'] if opts.has_key('smtp') and opts['smtp'].has_key('fromEmail') else None
        
        # Error handler
        self.onError = opts['onError'] if opts.has_key('onError') else None

        # Set logging
        if opts.has_key('loglevel'):
            logDict = {'info': logging.INFO, 'warning': logging.WARNING, 'debug': logging.DEBUG, 'none': logging.NOTSET}
            level = logDict[opts['loglevel']]
        else:
            level = logging.INFO
        format = ('%(asctime)s [%(levelname)s] %(message)s')
        logging.basicConfig(level=level,format=format)

    # Our main function - configures and starts the server (can also set options at this point)
    def listen(self, opts={}):
        global port, ip

        self.setOptions(opts)
        
        # Configure and start server
        reqHandler = WozzitRequestHandler
        reqHandler.parentSvr = self
        httpd = HTTPServer((self.ip, self.port), reqHandler)
        self.ip = '*' if self.ip == '' else self.ip 
        logging.info('Wozzit Node listening on %s:%s', self.ip, str(self.port))

        try:
            httpd.serve_forever()

        except KeyboardInterrupt:
            logging.info('^C received, shutting down the web server')
            httpd.socket.close()

    # Send a message to another node
    def send(self, msg, to):

        # Send request
        logging.info('Sending to %s', to)
        try:
            r = requests.post(url = to, json = msg.toDict())
            if r.status_code != 200:
                logging.warn('Failed to send: %s', r.status_code)
                if(self.onError is not None):
                    self.onError('send', r)
        except:
            logging.error('Unable to connect to server')
            if(self.onError is not None):
                self.onError('noserver', r)
            return False

        # Attempt to parse response into message
        logging.debug(r)
        try:
            json = r.json()
            logging.debug(json)
        except:
            logging.error('Invalid JSON returned')
            if(self.onError is not None):
                self.onError('invalidresponse', r)
            return False

        response = message.Message(json)

        return response

    # Validate incoming data and then work out how to respond
    def processActions(self, raw_data, ip):

        # Parse the message
        msg = message.Message()
        result = msg.loads(raw_data, ip)

        if result != True:
            logging.warning('Rejecting message: %s', result.payload['message'])
            return result
        
        logging.debug('Message accepted')
        logging.debug(msg.toJSON())
            
        if len(self.actions) == 0:
            logging.debug('No actions')
            return message.NotImplementedMessage()
        
        # Go through each action and make sure all criteria match
        for action in self.actions:
            logging.debug('Testing action %s', action['action'])
            if self.__actionMatch(action['match'], msg):
                logging.debug('Matched action %s', action['action'])
                self.__processAction(action, msg)
        return message.ReceiptMessage()

    # Perform actions. We have some built-in but mostly it will be callbacks
    def __processAction(self, action, msg):
        if action['action'] == 'log':
            self.__log(msg.toJSON())
        elif action['action'] == 'cb':
            logging.debug('Invoking callback')
            action['cb'](action, msg)
        elif action['action'] == 'forward':
            self.__forward(action, msg)
        elif action['action'] == 'desktop':
            self.__desktopNotification(action, msg)
        elif action['action'] == 'email':
            self.__sendEmail(action, msg)

    # Go through each action condition and make sure all match before processing further
    def __actionMatch(self, match, msg):

        if match != '*':
            for key, value in match.iteritems():
                if hasattr(msg, key) == False or getattr(msg, key) != value:
                    logging.debug('Failed action condition %s = %s', key, value)
                    return False
                logging.debug('Matched action condition %s = %s', key, value)
        else:
            logging.debug('Matched on wildcard')

        return True


    # Add event listeners
    def addLog(self, match="*"):
        self.actions.append({'match': match, 'action': 'log'})

    def addListener(self, match="*", callback=None):
        self.actions.append({'match': match, 'action': 'cb', 'cb': callback})

    def addForwarder(self, match, to):
        self.actions.append({'match': match, 'action': 'forward', 'to': to})

    def addDesktopNotification(self, match, message):
        self.actions.append({'match': match, 'action': 'desktop', 'message': message})

    def addEmail(self, match, toName, toEmail, subject, message):
        self.actions.append({'match': match, 'action': 'email', 'toName': toName, 'toEmail': toEmail, 'subject': subject, 'message': message})


    # Built-in actions
    def __log(self, s):
        print '[wozzit] ' + s

    def __forward(self, action, msg):
        global onError
        logging.info('Forwarding message to %s', action['to'])
        data = msg.toDict()
        r = requests.post(url = action['to'], json = data)
        if r.status_code != 200:
            logging.warn('Failed to forward: %s', r.status_code)
            logging.debug(r)
            if(self.onError is not None):
                self.onError('forward', r)

    def __desktopNotification(self, action, msg):
        logging.info('Triggering desktop notification')
        if platform.system() == 'Darwin':
            pync.notify(action['message'], title='Wozzit', sound='default')
        elif platform.system() == 'Windows':
            toaster = ToastNotifier()
            toaster.show_toast("Wozzit", action['message'])
        elif platform.system() == 'Linux':
            notify2.init('Wozzit')
            n = notify2.Notification('Wozzit', action['message'])
            n.show()

    def __sendEmail(self, action, msg):
        self.sendEmail(action['toName'], action['toEmail'], action['subject'], action['message'])

    def sendEmail(self, toName, toEmail, subject, body):

            if self.smtp['host'] is None:
                logging.warn('SMTP not configured')
                return

            if self.smtp['SSL'] == True:
                mta = smtplib.SMTP_SSL(self.smtp['host'], self.smtp['port'])
            else:
                mta = smtplib.SMTP(self.smtp['host'], self.smtp['port'])

            if self.smtp['username'] != None and self.smtp['password'] != None:
                mta.login(self.smtp["username"], self.smtp["password"])

            mime = MIMEMultipart()
            mime['From'] = self.smtp['fromName'] + " <" + self.smtp['fromEmail'] + ">"
            mime['To'] = toName + " <" + toEmail + ">"
            mime['Subject'] = subject
            mime.attach(MIMEText(body, 'plain'))
            msgText = mime.as_string()
            
            try:
                mta.sendmail(self.smtp['fromEmail'], toEmail, msgText)
                logging.info('Email sent to ' + toEmail)
            except:
                e = sys.exc_info()[0]
                logging.error('Failed to send email: ' + str(e))

