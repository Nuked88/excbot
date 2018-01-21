//var webfolder = new static.Server('./web');

const express = require('express');
const app = express();
var jade = require('jade');
var config = require('./config')
var expressMongoDb = require('express-mongo-db');


app.use(expressMongoDb(config.database.url));

var bodyParser = require('body-parser')

var apiController = require('./controllers/api');
var index = require('./controllers/index')
// parse requests of content-type - application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())
app.set('view engine', 'jade');

app.get('/api/data/:id', apiController.getRecentDeviceTemps);
app.get('/api/symlist', apiController.getListSym);
// define a simple route
app.use('/', express.static('web/AdminLTE/'));

app.listen(8080, () => {
    console.log('listening on 8080')
})

