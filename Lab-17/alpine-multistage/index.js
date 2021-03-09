'use strict';

const express = require('express');

// Constants
const PORT = 3000;
const HOST = '0.0.0.0';

// App
const app = express();
app.get('/', (req, res) => {
  res.send('Hello \n\n');
});

app.listen(PORT, HOST);
console.log('http://'+HOST+':'+PORT + '\n\n');
