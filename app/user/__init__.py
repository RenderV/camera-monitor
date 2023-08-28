def create_module(app):
    from .views import user_bp, gen_pass
    from .models import User

    user = User.objects(email="admin@admin.com")
    if not user and app.config.get('CREATE_TEST_ADMIN'):
        user = User(
            password=gen_pass('admin'),
            email='admin@admin.com',
            username='admin',
            admin=True
        )
        user.save()
        print('Created test admin')
    app.register_blueprint(user_bp, url_prefix="/user/")