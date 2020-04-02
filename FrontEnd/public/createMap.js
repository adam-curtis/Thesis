'use strict'
// var R = require("r-script");
function createMap() {
    console.log('g');
    var out = R("test.py")
        .data("hello world")
        .callSync();
    console.log(out);
}