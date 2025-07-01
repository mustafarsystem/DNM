from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, URL



# WTForm for creating a blog post
class FirmaForm(FlaskForm):
    unvan = StringField("Firma Ünvanı", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Submit Post")




# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email=StringField("Email", validators=[DataRequired()])
    password=PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')



class FirmForm(FlaskForm):
    name = StringField("Firma Ünvanı", validators=[DataRequired()])
    vergi_no = StringField("Vergi No", validators=[DataRequired()])
    vergi_d =  StringField("Vergi Dairesi", validators=[DataRequired()])
    adres = StringField("Adres", validators=[DataRequired()])
    ilgili = StringField("İlgili Kişi", validators=[DataRequired()])
    submit = SubmitField("Onayla")

class SiparisForm(FlaskForm):
    firma = SelectField("Firma", validators=[DataRequired()])
    sip_no = StringField("Sipariş No", validators=[DataRequired()])
    sip_rev = StringField("Sipariş Rev", validators=[DataRequired()])
    ilgili = StringField("İlgili Kişi", validators=[DataRequired()])
    sip_trh = DateField('Sipariş Tarihi', format='%Y-%m-%d', validators=[DataRequired()])
    teklif_no = StringField("Teklif No", validators=[DataRequired()])
    satır_no = StringField("Satır No", validators=[DataRequired()])
    urun_kodu = StringField("Ürün Kodu", validators=[DataRequired()])
    teknik_res_no = StringField("Teknik Resim No", validators=[DataRequired()])
    rev_no = StringField("Rev No", validators=[DataRequired()])
    urun_adi = StringField("Ürün Tanımı", validators=[DataRequired()])
    adet = IntegerField('Adet', validators=[DataRequired()])
    termin = DateField('Termin Tarihi', format='%Y-%m-%d', validators=[DataRequired()])
    kalifikasyon = SelectField("Kalifikasyon", validators=[DataRequired()])
    kal_class = SelectField("Kalite Sınıfı", validators=[DataRequired()])
    submit = SubmitField("Onayla")