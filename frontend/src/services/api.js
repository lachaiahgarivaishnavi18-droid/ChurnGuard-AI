let token=sessionStorage.getItem('churnguard_token');
const base=import.meta.env.VITE_API_URL||'';
export const authorized=()=>Boolean(token);
export function setToken(value){token=value; value?sessionStorage.setItem('churnguard_token',value):sessionStorage.removeItem('churnguard_token');}
export async function api(path,options={}){
 const response=await fetch(base+'/api'+path,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`} :{}),...options.headers}});
 if(response.status===204)return null;
 const type=response.headers.get('content-type')||'';
 if(!type.includes('application/json'))throw new Error('The banking API is not connected to this deployment yet.');
 const data=await response.json();
 if(!response.ok){const error=new Error(data.error||data.msg||'Request failed');error.status=response.status;throw error;}
 return data;
}
export const post=(path,body={})=>api(path,{method:'POST',body:JSON.stringify(body)});
