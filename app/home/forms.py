from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,FileField,TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email, Regexp
from app.models import User, Tag

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
            "class": "user_login_btn"
        }
    )

    def validate_account(self, field):
        account = field.data
        id = User.query.filter_by(id=account).count()
        if id == 0:
            raise ValidationError("账号不存在！")


class RegistForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称!")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入昵称",
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
            "id": "pw1",
            "placeholder": "请输入密码!",
        }
    )

    repwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired(message="确认密码!"),
            EqualTo("pwd", message="两次密码不一致")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control",
            "id": "pw2",
            "placeholder": "确认密码!",
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱!"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱",
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机号!"),
            Regexp("1[0-9]{10}", message="手机格式不正确")

        ],
        description="手机",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机号",
        }
    )

    submit = SubmitField(
        '注册',
        render_kw={
            "class": "regist_btn"
        }
    )


    def validate_name(self,field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 1:
            raise ValidationError("昵称已经存在")
    def validate_email(self,field):
        email = field.data
        email = User.query.filter_by(email=email).count()
        if email == 1:
            raise ValidationError("邮箱已经存在")

    def validate_phone(self, field):
            phone = field.data
            phone = User.query.filter_by(phone=phone).count()
            if phone == 1:
                raise ValidationError("手机已经存在")

class UserdetailForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称!")
        ],
        description="昵称",
        render_kw={
            "class": "personal_name_change",
            "placeholder": "请输入昵称",
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱!"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "personal_email_change",
            "placeholder": "请输入邮箱",
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机号!"),
            Regexp("1[0-9]{10}", message="手机格式不正确")

        ],
        description="手机",
        render_kw={
            "class": "personal_phone_change",
            "placeholder": "请输入手机号",
        }
    )
    face = FileField(
        label="头像",
        validators=[
        ],
        description="头像",
        render_kw={
            "id":"face_change",
            "onchange":"handleFiles(this,'icon')"
        }
    )
    info = TextAreaField(
        label="个人介绍",
        validators=[
        ],
        description="简介",
        render_kw={
            "id":"personal_introduce_text_control",
            "maxlength":"80",
            "placeholder":"个人介绍",
            "rows":"5",
            "cols":"50"
        }
    )
    submit = SubmitField(
        '修改',
        render_kw={
            "class": "personal-info-change"
        }
    )

class PasswordChangeForm(FlaskForm):
    oldpwd = PasswordField(
        label="密码",
        validators=[
            DataRequired(message="请输入旧密码!")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "id": "pw_check",
            "placeholder": "旧密码!",
        }
    )

    newpwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired(message="请输入新密码"),
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "id": "pw_new",
            "placeholder": "新密码",
        }
    )
    submit = SubmitField(
        '确认密码',
        render_kw={
            "class": "personal-info-change"
        }
    )

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

class CommentForm(FlaskForm):
    comment = TextAreaField(
        label="评论",
        validators=[
            DataRequired("评论不能为空")
        ],
        description="评论",
        render_kw={
            "id": "personal_comment_text_control",
            "maxlength": "80",
            "placeholder": "评论",
            "rows": "5",
            "cols": "50"
        }
    )
    submit = SubmitField(
        '提交',
        render_kw={
            "class": "personal-info-change"
        }
    )
