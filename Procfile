web: bin/start-pgbouncer bin/start-nginx-debug bundle exec unicorn -c config/unicorn.rb daphne -p $PORT --bind 0.0.0.0 -v2 Me2U.asgi:application
