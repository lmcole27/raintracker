from flask import Flask, render_template, url_for, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TelField
from wtforms.validators import DataRequired
# from flask_wtf.csrf import CSRFProtect
import requests 
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()


#CREATE WEBAPP
app = Flask(__name__)

#SECRET KEY FOR FLASK
SECRET_KEY = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY
# app.config['WTF_CSRF_SECRET_KEY']="a csrf secret key"
# csrf = CSRFProtect(app)

#ENDPOINT INFORMTION FOR API
ACCOUNT_SID = os.environ.get('ACCOUNT_SID') 
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
client = Client(ACCOUNT_SID, AUTH_TOKEN)
wds_auth = os.environ.get('WDS_AUTH')
from_tel = os.environ.get('from_tel')

#INPUT FORM
class rainForm(FlaskForm):
    city = StringField('City', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    phone_no = TelField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

#WEB HOME PAGE
@app.route('/', methods=['GET', 'POST'])
def welcome():
    form = rainForm()

    if request.method == "POST":
                
        #CONVERT TO LOWERCASE
        location = (str(request.form["city"]) + "," + str(request.form["country"])).lower()
        to_tel = request.form["phone_no"]

        #BUILD THE ENDPOINT
        WDS_ENDPOINT = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast?locations="+ location + "&aggregateHours=24&forcastDays=1&unitGroup=us&shortColumnNames=true&contentType=json&key=" + wds_auth

        #FIND THE WEATHER
        response = requests.get(url=WDS_ENDPOINT)

        try: 
            data = response.json()
            precipitation = data['locations'][location]['values'][0]['pop']
        
        except:
            flash("Hmmm... we can't find that city. Please try again.") 
            return redirect(url_for('welcome'))
    
        else: 
            #LOGIC FOR RAIN/UMBRELLA
            if precipitation >50:
                content = "Bring an Umbrella in " + request.form["city"] + "!"
            else:
                content = "No rain today in " + request.form["city"] + "!"
    
            try:
                #SEND THE NOTIFICATION TO YOUR DEVICE USING TWILIO
                message = client.messages \
                                .create(
                                        body=content,
                                        from_=from_tel,
                                        to=to_tel
                                    )

            except:
                flash("Hmmm... we can't reach that telephone number. Please try again.") 
                return redirect(url_for('welcome'))              

            else: 
                flash("Sent! Check your messages."
                      )
            finally:
                return redirect(url_for('welcome'))
            
        finally:
            return redirect(url_for('welcome'))
        
    return render_template("index.html", form=form) 


#RUN THE WEBAPP
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)