ROOT=$(dirname $0)
# use .env_* or supply your own.
DOT_ENV=".env_symmetric"

function usage() {
  echo "usage: $0 [options ...]"
  echo "options:"
  echo "  -e <.env file>"
  exit 2
}

while getopts e:? arg; do
  case ${arg} in
    e) DOT_ENV=${OPTARG};;
    ?) usage;;
  esac
done

pushd ${ROOT} > /dev/null
cp ${DOT_ENV} .env
npm start

popd > /dev/null
