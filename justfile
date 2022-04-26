alias r := run
alias m := manage
alias t := test
alias wt := watch-test

set dotenv-load := true
set positional-arguments := true

dbuild:
  docker build .

dcbuild:
  docker-compose build --parallel app

@run *args='':
  docker-compose run app "$@"

@manage *args='':
  just run python manage.py "$@"

@test *args='.':
  just manage test "$@"

@watch-test *args='.':
  watchexec -w=app/ -- just test "$@"
