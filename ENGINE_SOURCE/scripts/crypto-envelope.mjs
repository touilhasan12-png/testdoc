// Hybrid RSA-OAEP + AES-256-GCM envelope; no third-party crypto dependency.
import {createCipheriv, createDecipheriv, publicEncrypt, privateDecrypt, randomBytes, constants} from 'node:crypto';
import {readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';

export function seal(bytes, publicKey) {
  const key=randomBytes(32),iv=randomBytes(12);
  const cipher=createCipheriv('aes-256-gcm',key,iv);
  const encrypted=Buffer.concat([cipher.update(bytes),cipher.final()]);
  const wrapped=publicEncrypt({key:publicKey,oaepHash:'sha256',padding:constants.RSA_PKCS1_OAEP_PADDING},key);
  const header=Buffer.from(JSON.stringify({v:1,alg:'RSA-OAEP-SHA256/AES-256-GCM',key:wrapped.toString('base64'),iv:iv.toString('base64'),tag:cipher.getAuthTag().toString('base64')}));
  const prefix=Buffer.alloc(4);prefix.writeUInt32BE(header.length);
  return Buffer.concat([prefix,header,encrypted]);
}
export function open(bytes, privateKey) {
  const n=bytes.readUInt32BE(0);
  if(n<32||n>8192||bytes.length<4+n)throw Error('Invalid envelope header');
  const h=JSON.parse(bytes.subarray(4,4+n));
  if(h.v!==1||h.alg!=='RSA-OAEP-SHA256/AES-256-GCM')throw Error('Unsupported envelope');
  const key=privateDecrypt({key:privateKey,oaepHash:'sha256',padding:constants.RSA_PKCS1_OAEP_PADDING},Buffer.from(h.key,'base64'));
  const cipher=createDecipheriv('aes-256-gcm',key,Buffer.from(h.iv,'base64'));cipher.setAuthTag(Buffer.from(h.tag,'base64'));
  return Buffer.concat([cipher.update(bytes.subarray(4+n)),cipher.final()]);
}
if(process.argv[1]&&fileURLToPath(import.meta.url)===resolve(process.argv[1])){
  const [op,source,dest,keyFile]=process.argv.slice(2);
  if(!['seal','open'].includes(op)||!source||!dest||!keyFile)throw Error('Usage: node crypto-envelope.mjs seal|open source destination key.pem');
  const bytes=readFileSync(source),key=readFileSync(keyFile,'utf8');
  writeFileSync(dest,op==='seal'?seal(bytes,key):open(bytes,key),{mode:0o600});
  console.log(`Envelope ${op} complete.`);
}
