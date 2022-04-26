alias r := run
alias m := manage
alias t := test
alias wt := watch-test

set dotenv-load := true
set positional-arguments := true

@run *args='':
  docker-compose run app "$@"

@manage *args='':
  just run python manage.py "$@"

@test *args='.':
  just manage test "$@"

@watch-test *args='.':
  watchexec -w=app/ -- just test "$@"
