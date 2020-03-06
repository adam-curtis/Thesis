'use strict'

const express = require('express');
const morgan = require('morgan');

const app = express();

app.use(morgan('dev'));
app.use(express.static('public'));

app.get(`/`, (req, res) => {
            
    res.redirect('login');
});

app.use( (req,res) => {
    res.status(404).send(`The url: ${req.url} cannot be found.`);
});

app.listen(1068, () => console.log('The server is up and running...'));