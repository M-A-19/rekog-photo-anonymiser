"use strict";
(function(window,AWS,undefined) {

    // private properties
    var functionname = "rekogFaceAnon",
        myRegion = 'eu-west-2',
        IdentityPoolId = 'eu-west-2:5f4fed45-de99-4442-9ee3-948b430bcc45';

    AWS.config.update({
        region: myRegion,
        credentials: new AWS.CognitoIdentityCredentials({
            IdentityPoolId: IdentityPoolId
        }),
        convertResponseTypes: !1,
    });

    var lambda = new AWS.Lambda();
    var slideshow = new Slideshow();


    /**
     * Bind the thumbnail behaviour to passed html elements.
     *
     * @param {HTMLCollection} thumbs A collection of Html elements.
     *
     * @returns {void}
     */
    function bindThumbs(thumbs) {
        var end = thumbs.length;
        for (var i = 0; i < end; i++) {
            thumbs[i].addEventListener("click", createthumbbehaviour(i));
        }
    }

    /**
     * Bind the slide behaviour to passed html elements.
     *
     * @param {HTMLCollection} col A collection of Html elements.
     *
     * @returns {void}
     */
    function bindSlides(col){
        slideshow.initslides(col);
    }

    // private methods

    /**
     * Create a behaviour( closure to bind to the thumbnail buttons.
     *
     * @param {number} i Numeric index for thumbnail.
     *
     * @returns {Function}
     */
    function createthumbbehaviour(i) {
        var photoname = "wikipeople" + (i + 1);
        return function(event) {
            slideshow.hideslides();
            displayloader(true);
            event.preventDefault();
            var params = {
                FunctionName: functionname,
                Payload: '{"photo_name": "' + photoname + '.jpg" }'
            };
            lambda.invoke(params, function (err, data) {
                if (err) {
                    displayloader(false);
                    console.log(err, err.stack); // an error occurred
                }
                else {
                    // successful response
                    var response = JSON.parse(data.Payload);
                    console.log(response);
                    displayresult(response);
                    displayloader(false);
                    slideshow.startslides();
                }
            });


        };
    };

    /**
     * populate DOM with values from the lambda operation.
     *
     * @param {object} info object containing values from the lambda operation.
     *
     * @returns {void}
     */
    function displayresult (info) {
        var d = new Date();

        window.document.getElementById('jobtime').innerHTML = info.jobtime + "ms";
        window.document.getElementById('facecount').innerHTML = info.facecount;
        window.document.getElementById('outputMain').src = 'http://' + info.result_uri + '?' + d.getSeconds();

    }

    /**
     * Handle the loader element display.
     *
     * @param {boolean} bool Display the loader?
     *
     * @returns {void}
     */
    function displayloader (bool) {
        window.document.getElementById('loader').style.display = (bool)?'block':'none';
    }

    /**
     * Slideshow class.
     *
     * @constructor
     */
    function Slideshow () {

        /**
         * Iterable collection of HTMLElements, one for each slide.
         *
         * @type {Array}
         */
        var slides =[];
        /**
         * Position of current slide in the list.
         *
         * @type {number}
         */
        var slideindex = 0;
        /**
         * Interval id of the process handling the slide transition.
         *
         * @type {number}
         */
        var slideint = 0;

        /**
         * Initialise the slideshow with a collection of slide elements.
         *
         * @param {HTMLCollection} col A collection of Html elements.
         *
         * @returns {void}
         */
        this.initslides = function (col) {
            slides = col;

        };
        /**
         * Start the slideshow.
         *
         * @returns {void}
         */
        this.startslides = function () {

            slideindex=1;
            this.nextslide();
            slideint = setInterval(this.nextslide.bind(this), 3000);
        };
        /**
         * Hide all slideshow content.
         *
         * @returns {void}
         */
        this.hideslides = function () {
            var end = slides.length;
            for (var i = 0; i < end; i++) {
                slides[i].style.display = "none";
            }
        };
        /**
         * Reveal the next slide in the list.
         *
         * @returns {void}
         */
        this.nextslide = function () {
            this.hideslides();
            slides[slideindex].style.display = "block";
            if (slideindex +1 >= slides.length) {
                clearInterval(slideint);
                slideindex=0;
            } else {
                slideindex++;
            }
        }
    }

    // reveal module.
    window.anony = {
        bindThumbs: bindThumbs,
        bindSlides: bindSlides,
    };
})(window, AWS);


document.addEventListener('DOMContentLoaded', function (){
    anony.bindThumbs(document.getElementsByClassName("img-hover-zoom"));
    anony.bindSlides(document.getElementsByClassName("slide"));
});
