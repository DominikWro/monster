from flask import Flask
from flask import render_template
from flask import jsonify
from flask import session
from flask import redirect
from flask import request
from multiprocessing import Process
from time import sleep
from time import time


class Artist(object):

    def __init__(self, diary, config_opts):

        self.diary = diary

        app = Flask(
            __name__,
            template_folder='../assets/templates',
            static_folder='../assets/static',
            static_url_path=''
        )
        app.diary = diary
        app.secret_key = "Alice touches herself."
#        app.debug = True

        if config_opts.has_option('overall', 'password'):
            app.password = config_opts.get('overall', 'password')

            @app.before_request
            def check_auth():
                if request.endpoint not in ('check_password', 'static'):
                    if 'is_logged_in' not in session:
                        return redirect('/password')
        else:
            app.password = None

        # See if configured to bind to specific address/port
        if config_opts.has_option('overall', 'bind'):
            bind_opt = config_opts.get('overall', 'bind')
            if ':' in bind_opt:
                # e.g bind = 127.0.0.1:4567
                app.bind_addr, app.bind_port = bind_opt.split(':')
                app.bind_port = int(app.bind_port)
            else:
                # eg. bind = 127.0.0.1
                app.bind_addr = bind_opt
                app.bind_port = 5000

        else:
            app.bind_addr = '127.0.0.1'
            app.bind_port = 5000

        app.enabled_probes = config_opts.options('probes')
        # I can split too!
        # Since I can't do an "IF osx.LoadAVG OR linux.LoadAvg in Jinja
        # I had to come up with this, remove their OS-prefixs
        app.enabled_probes = [x.split('.')[1] for x in app.enabled_probes]

        @app.route('/')
        def index():
            return render_template(
                'index.html',
                enabled_probes=app.enabled_probes,
                password=app.password
            )

        @app.route('/api/load/<path:mode>')
        def api_load(mode):
            load_record = app.diary.read('LoadAvg', mode, how_many = 200)
            return jsonify({
                'load': load_record,
            })

        @app.route('/api/heavy_process_stat')
        def api_heavy_process_stat():
            heavy_process_stat = app.diary.read(
                'HeavyProcessStat','live', how_many=1)[0]
            return jsonify(heavy_process_stat)

        @app.route('/api/mem_info/<int:how_many>')
        def api_mem_info(how_many=200):
            mem_info_record = app.diary.read('MemInfo', 'live', how_many)
            return jsonify({
                'mem_info': mem_info_record,
            })

        @app.route('/api/apache')
        def api_apache():
            apache_activity = app.diary.read('Apache2', 'live', how_many = 50)

            return jsonify({
                'apache_activity': apache_activity
            })

        @app.route('/api/apache_geocache')
        def api_apache_geocache():
            apache_ips = app.diary.read('Apache2', 'live', how_many=1)[0]
            return jsonify({
                'apache_ips': {
                    "ips": apache_ips["ips"]
                }
            })

        @app.route('/api/postgres/<int:how_many>')
        def api_postgres(how_many=30):
            postgres_stats = app.diary.read('Postgres', 'live', how_many)
            return jsonify({
                'postgres_stats': postgres_stats,
            })

        @app.route('/api/mysql')
        def api_mysql():
            mysql_stats = app.diary.read('MySQL', 'live', how_many = 50)
            return jsonify({
                'mysql_stats': mysql_stats,
            })

        @app.route('/api/nginx/<int:how_many>')
        def api_nginx(how_many=30):
            nginx_stats = app.diary.read('Nginx','live', how_many)
            return jsonify({
                'nginx_stats': nginx_stats,
            })

        @app.route('/api/nginx_geocache')
        def api_nginx_geocache():
            nginx_ips = app.diary.read('Nginx','live', how_many=1)[0]
            return jsonify({
                'nginx_ips': {
                    "ips": nginx_ips.get("ips", [])
                }
            })

        @app.route('/password', methods=['GET', 'POST'])
        def check_password():
            if request.method == 'POST':
                if request.form['password'] == app.password:
                    session['is_logged_in'] = 'uh-uh!'
                    return redirect('/')
                else:
                    return render_template('password.html', message="Nope, that's not it.")
            else:
                return render_template('password.html')

        @app.route('/logout')
        def logout():
            session.clear()
            return redirect('/password')

        # Assign to self, so other methods can interact with it.
        self.app = app

    def start(self):

        self.flask_ps = Process(
            target=self.app.run,
            kwargs={'host': self.app.bind_addr, 'port': self.app.bind_port}
        )
        self.flask_ps.start()

    def stop(self):
        print "Stop called @", time()
        sleep(1)
        print "[!] Telling the artist to pack his things.."
        self.flask_ps.terminate()
