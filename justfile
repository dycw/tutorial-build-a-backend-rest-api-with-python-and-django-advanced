alias r := run
alias t := test
alias wt := watch-test

set dotenv-load := true
set positional-arguments := true

@run *args='':
  docker-compose run app "$@"

test:
  just run python manage.py test

watch-test:
  watchexec -w=app/ -- just test
