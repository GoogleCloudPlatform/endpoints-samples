var express = require('express');
var passport = require('passport');
var ensureLoggedIn = require('connect-ensure-login').ensureLoggedIn()
var router = express.Router();

//===========================================================
// Please change below according to your API configuration.
var API_HOST = 'https://endpoints-bookstore-node.appspot.com';
var API_PATH = '/shelves/1';
var API_URL = API_HOST + API_PATH;
//===========================================================

function makeRequest(url, user, res) {
  var request = require('request');
  request.get(
    { url : url,
      headers: { 'Authorization': 'Bearer ' + user.token }
    },
    function (error, response, body) {
      res.render('user', { user: user, res: error || response.body});
    }
  );
}

/* GET user profile and make API call. */
router.get('/', ensureLoggedIn, function(req, res, next) {
  makeRequest(API_URL, req.user, res)
});

module.exports = router;
