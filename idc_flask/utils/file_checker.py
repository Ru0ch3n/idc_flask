ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# 判断上传资源是否合法安全，否则容易出现文件上传绕过、XSS与恶意命令执行。
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
