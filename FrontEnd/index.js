'use strict'

const express = require('express');
const spawn = require('child_process').spawn;
const morgan = require('morgan');
const bodyParser = require('body-parser');
const app = express();
app.use(morgan('dev'));
app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

function completeRScript(country, date, res) 
{

    var child = spawn('Rscript', ['test.R', "\""+country+"\"", date]);
    console.log("Rscript hdfCreation.R \""+country+"\"" + date);
    child.stdout.on('data', function(data) {
        console.log(data.toString()); 
    });
    
    child.stderr.on('data', function(data) {
        console.error(data.toString());
    });

    child.on('exit', function(code) {
        console.log("Exited with code " + code);
    });
}

app.get('/',function(req,res) {
    res.sendFile('public/data.html' , { root : __dirname});
});

app.post('/model.html', async (req, res) => {
    var date = req.body.date;
    var country = req.body.country;
    console.log(date, country);
    completeRScript(country,date, res);
    res.json();
});

app.use( (req,res) => {
    res.sendStatus(404);
});

app.listen(1068, () => console.log('The server is up and running...'));

