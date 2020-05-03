'use strict'

const express = require('express');
const spawnSync = require('child_process').spawnSync;
const morgan = require('morgan');
const bodyParser = require('body-parser');
const app = express();
app.use(morgan('dev'));
app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

async function completeRScript(projectName, date, res) 
{
    var id = "";
    console.log("Creating Map");
    let result = spawnSync('Rscript', ['hdfCreation.R', projectName, date], {
        shell: true, encoding : 'utf8'
    });
    id = result.stdout;
    console.log(result.stdout);
    console.log(result.stderr);
    console.log("Finished Map Creation");
    return id;
}

app.get('/',function(req,res) {
    res.sendFile('public/homePage.html' , { root : __dirname});
});

app.post('/model.html', async (req, res) => {
    var date = req.body.date;
    var projectName = req.body.projectName;
    var ret;

    try {
        ret = await completeRScript(projectName,date,res);
    }
    catch(e) {
        console.log('Catch an error: ', e)
    }
    var idStart = ret.lastIndexOf("]");
    ret = ret.substr(idStart+1);
    ret = ret.replace("\"","");
    ret = ret.replace(" ","");
    ret = ret.replace("\"","");
    console.log(ret);
    res.json(ret);
});

app.use( (req,res) => {
    res.sendStatus(404);
});

app.listen(1068, () => console.log('The server is up and running...'));