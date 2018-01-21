var express = require('express')
var app = express()
app.set('view engine', 'jade');
var router = express.Router();


router.getRecentDeviceTemps = function(req, res) {

     req.db.collection('data').aggregate([
    { "$match": { "sym": req.params.id } },
    { "$project": {
        "year": { "$year": '$date'},
        "month": { "$month": '$date'},
        "day": { "$dayOfMonth": '$date'},
        "hour": { "$hour": '$date'},
        "minute": { "$minute": '$date'},
        "price": 1
 
    }},

    {
        "$group": {
        _id: { year: '$year', month: '$month', day: '$day', hour: '$hour', minute: '$minute'},
        price:{
            "$avg": "$price"
        }}
    },
    {
        "$limit":40
    }

   
]).toArray(function(err, results) {
         if (err) {
             next(err);
         }
 
         res.format({
             // Respond to normal browser requests with the 404 page
             html: function() {
                 res.render('404', {
                     title: 'Page not found'
                 });
             },
 
             // Respond to AJAX requests with Morris-consumable data
             html: function() {
                 // Initialise an array for returning later
                 var graphData = [];
 
                 // Go through each result
                 for (var i = 0; i < results.length; i++) {
                     var result = results[i];
                    // console.log(result);
                     // Check these results are valid 
                     if (result._id && result.price) {
                         var id= result._id;
                         //2018-01-14T19:52:16.190Z
                        // var ndate = id['year']+'-'+id["month"]+'-'+id["day"]+'T'+id["hour"]+':00:00.190Z';

                         //console.log(ndate);
                         var date = new Date(id['year'], id["month"], id["day"], id["hour"], id["minute"], "00", "000")
                         var price = result.price;
                         
                         // Create an object for Morris.js to read     
                         var graphPoint = {};
                         graphPoint.timestamp = date.getTime();
                         graphPoint.price = price;
 
                         // Push the object to the array for returning     
                         graphData.push(graphPoint);
                     }
                 }
                 // Return the graphData object as JSON    
                 res.json({
                     graphData: graphData
                 });
             }
         });
     });
 };



 router.getListSym = function(req, res) {
    //console.log(temp);
     // Make the call to MongoDB to grab the relevant records
    // console.log(req);

     req.db.collection('data').aggregate([{$group: { _id: '$sym'} }],{sort: {'sym': -1 }}, function(err, results) {
         if (err) { 
             next(err);
         }
        
         res.format({
             //// Respond to normal browser requests with the 404 page
             //html: function() {
             //    res.render('404', {
             //        title: 'Page not found'
             //    });
             //}, 
 
             // Respond to AJAX requests with Morris-consumable data
             html: function() {
                 // Initialise an array for returning later
                 var graphData = [];
 
                 // Go through each result
                 for (var i = 0; i < results.length; i++) {
                     var result = results[i];
                     //console.log(result);
                     // Check these results are valid    
                     if (result._id) {
                         
                         var symb = result._id;
                         // Create an object for Morris.js to read     
                         var graphPoint = {};
                         graphPoint.symb = symb;
 
                         // Push the object to the array for returning     
                         graphData.push(graphPoint);
                     }
                 }
                 // Return the graphData object as JSON    
                 res.json({
                    graphData
                 });
             }
         });
     });
 };

 module.exports = router;