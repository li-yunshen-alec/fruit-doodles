(function()
{
	$(document).ready(function() {

		var canvas = document.querySelector("#canvas");
		var context = canvas.getContext("2d");
		var navbar = document.querySelector(".navbar");

		canvas.width = window.innerWidth;
		canvas.height = window.innerHeight - navbar.offsetHeight;

		var Mouse = { x: 0, y: 0 };
		var lastMouse = { x: 0, y: 0 };
		context.fillStyle="white";
		context.fillRect(0,0,canvas.width,canvas.height);
		context.color = "black";
		context.lineWidth = 5 * 2;
		context.lineJoin = context.lineCap = 'round';

		debug();

	canvas.addEventListener( "mousemove", function( e )
	{
		lastMouse.x = Mouse.x;
		lastMouse.y = Mouse.y;
	
		var rect = this.getBoundingClientRect();
		Mouse.x = e.clientX - rect.left;
		Mouse.y = e.clientY - rect.top;
	
	}, false );
		
	canvas.addEventListener( "mousedown", function( e )
	{
		canvas.addEventListener( "mousemove", onPaint, false );

	}, false );

	canvas.addEventListener( "mouseup", function()
	{
		canvas.removeEventListener( "mousemove", onPaint, false );
	
	}, false );
		
	var onPaint = function()
	{
		context.lineWidth = context.lineWidth;
		context.lineJoin = "round";
		context.lineCap = "round";
		context.strokeStyle = context.color;

		context.beginPath();
		context.moveTo( lastMouse.x, lastMouse.y );
		context.lineTo( Mouse.x, Mouse.y );
		context.closePath();
		context.stroke();
	};

	function debug()
	{
		/* CLEAR BUTTON */
		var clearButton = $( "#clearButton" );

		clearButton.on( "click", function()
		{

			// document.getElementById("chartContainer").style.display = "none";
			context.clearRect( 0, 0, 280 * 3, 280 * 3 );
			context.fillStyle="white";
			context.fillRect(0,0,canvas.width,canvas.height);


		});
		
		var eraseButton = $( "#eraseButton" );

		eraseButton.on( "click", function()
		{
			console.log('erasing');
			context.color = "white";
			context.lineWidth = 5 * 9;
		});
		
		var brushButton = $( "#brushButton" );

		brushButton.on( "click", function()
		{
			console.log('brushButton');
			context.color = "black";
			context.lineWidth = 5 * 2;
		});

		/* COLOR SELECTOR */

		$( "#colors" ).change(function()
		{
			var color = $( "#colors" ).val();
			context.color = color;
		});

		/* LINE WIDTH */

		$( "#lineWidth" ).change(function()
		{
			context.lineWidth = $( this ).val();
		});
	}
});
}());
