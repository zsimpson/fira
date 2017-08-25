// Inspired by hyperscript, with no dependencies and a bit simpler
function z() {
	var a = arguments[0];
	var m = a.split( /(?=[\.#])/g );
	var e = document.createElement( m[0] );
	m.slice(1).forEach( function (i) {
		var term = i.substring(1);
		if( i[0] === '.' ) {
			e.className += ' ' + term;
		}
		else if( i[0] === '#' ) {
			e.setAttribute( 'id', term );
		}
	});
	for( var i=1; i<arguments.length; i++ ) {
		var a = arguments[i];
		if( typeof a === 'string' ) {
			e.appendChild( document.createTextNode(a) );
		}
		else if( a instanceof Array ) {
			for( var j=0; j<a.length; j++ ) {
				if( typeof a[j] !== 'undefined' ) {
					e.appendChild( a[j] );
				}
			}
		}
		else if( a instanceof HTMLElement ) {
			e.appendChild( a );
		}
		else if( a instanceof Object ) {
			for( var key in a ) {
				if( a.hasOwnProperty(key) ) {
					if( key == 'data' ) {
						for( var d in a[key] ) {
							e.dataset[a[key][d].key] = a[key][d].val;
						}
					}
					else {
						e.setAttribute( key, a[key] );
					}
				}
			}
		}
	}
	return e;
}
