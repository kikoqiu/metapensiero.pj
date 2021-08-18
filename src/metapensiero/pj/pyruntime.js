export function *range(b,e,st=1){
    if(e===undefined){
        e=b;
        b=0;
    }
    for(let i=b;i<e;i+=st){
        yield i;
    }
}
export function* mapg(it, mappers, filters){
	if(mappers.length==1){
		for(let a of it){
			if(filters[0]!=null && !filters[0](a)){
				continue;
			}
			yield mappers[0](a);
		}
		return;
	}

	if(mappers.length==2){
		for(let a of it){
			if(filters[0]!=null && !filters[0](a)){
				continue;
			}
			for(let b of mappers[0](a)){
				if(filters[1]!=null && !filters[1](a,b)){
					continue;
				}
				yield mappers[1](a,b);
			}
		}
		return;
	}


	if(mappers.length==3){
		for(let a of it){
			if(filters[0]!=null && !filters[0](a)){
				continue;
			}
			for(let b of mappers[0](a)){
				if(filters[1]!=null && !filters[1](a,b)){
					continue;
				}
				for(let c of mappers[1](a,b)){
					if(filters[2]!=null && !filters[2](a,b,c)){
						continue;
					}
					yield mappers[2](a,b,c);
				}
			}
		}
		return;
	}

	throw new Error('not implemented');
}
export function mapl(it, mappers, filters){
	return [...mapg(it,mappers,filters)];
}

export function round(a){
	return Math.round(a);
}

export default function init(){
	console.log('init_runtime');
}

export function ext_acc(...acc) {
	var kwargs, last;
	last = acc.slice((- 1))[0];
	kwargs = null;
	if ((last instanceof kw)) {
		kwargs = last.values;
		return [acc.slice(0, (- 1)), kwargs];
	}
	return [acc];
}
export class dict {
	constructor(values) {
		this.values = values;
	}
	setdefault(key, val) {
		if ((! (key in this))) {
			this[key] = val;
		}
	}
}
export class kw extends dict{
}

export function staticmethod(f){
	return f;
}


export function pythonnew(cls,...args){
}
/*

def pythonset():
    return JS('new Set()')

def subscript(arr,lower,upper,step):
    return JS('new subscript()')
*/