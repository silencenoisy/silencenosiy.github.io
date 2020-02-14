from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,FileField,SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Admin, Tag

tags = Tag.query.all()


class LoginForm(FlaskForm):
    account = StringField(
        label="账号",
        validators=[
            DataRequired("用户名不能为空"),
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号",
            # "required": "required"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired(message="请输入密码!")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码!",
            # "required": "required"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "admin_login_btn"
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在！")

class MovieForm(FlaskForm):
    title = StringField(
        label="视频标题",
        validators=[
            DataRequired("请输入视频标题")
        ],
        description="视频标题",
        render_kw={
            "class": "personal_name_change",
            "id":"movie_title",
            "placeholder": "请输入标题",
        }
    )
    url = FileField(
        validators=[
            DataRequired("请上传文件")
        ],
        description="视频"
    )
    logo = FileField(
        label="封面",
        validators=[
        ],
        description="封面",
        render_kw={
            "id": "logo_change",
            "onchange": "handleFiles(this,'icon')"
        }
    )
    tag = SelectField(
        label="标签",
        validators=[
            DataRequired("请选择标签")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in tags],
        description="标签",

    )
    submit = SubmitField(
        '上传',
        render_kw={
            "class": "movie_submit"
        }
    )
