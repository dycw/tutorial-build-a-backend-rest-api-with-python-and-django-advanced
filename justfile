alias t := test
alias wt := watch-test

test:
  docker-compose run app python manage.py test

watch-test:
  watchexec -w=app/ -- docker-compose run app python manage.py test
