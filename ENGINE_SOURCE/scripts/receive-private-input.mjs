// Executed on a GitHub Actions runner. No project media or PAT is written to
// the public repository. The relay validates the GitHub OIDC token and encrypts
// input to this job's freshly generated RSA key. The token is never logged.
import {generateKeyPairSync} from 'node:crypto';
import {writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {open} from './crypto-envelope.mjs';
const url=process.env.RELAY_URL,token=process.env.RELAY_ID_TOKEN,tmp=process.env.RUNNER_TEMP;
if(!url||!token||!tmp)throw Error('Missing relay configuration or OIDC token');
const pair=generateKeyPairSync('rsa',{modulusLength:3072,publicKeyEncoding:{type:'spki',format:'pem'},privateKeyEncoding:{type:'pkcs8',format:'pem'}});
let data;
for(let attempt=0;attempt<20;attempt++){
 const response=await fetch(url+'/handshake',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id_token:token,public_key:pair.publicKey}),signal:AbortSignal.timeout(60000)});
 if(response.status===503){await new Promise(r=>setTimeout(r,3000));continue;}
 if(!response.ok)throw Error('Authenticated relay handshake failed: '+response.status);
 data=await response.json();break;
}
if(!data)throw Error('Relay handshake timed out');
const received=await fetch(url+'/payload',{signal:AbortSignal.timeout(180000)});
if(!received.ok)throw Error('Encrypted asset transfer failed: '+received.status);
const zip=open(Buffer.from(await received.arrayBuffer()),pair.privateKey);
await writeFile(join(tmp,'history-input.zip'),zip,{mode:0o600});
await writeFile(join(tmp,'history-output-public.pem'),data.output_public_key,{mode:0o600});
console.log('Authenticated and decrypted project inputs; private data will not be uploaded unencrypted.');
