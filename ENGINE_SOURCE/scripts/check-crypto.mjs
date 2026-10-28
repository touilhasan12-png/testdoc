import {generateKeyPairSync} from 'node:crypto';
import {seal,open} from './crypto-envelope.mjs';
const {publicKey,privateKey}=generateKeyPairSync('rsa',{modulusLength:2048});
const plain=Buffer.from('private test data'),cipher=seal(plain,publicKey);
if(!open(cipher,privateKey).equals(plain))throw Error('Encryption round-trip failed');
const tampered=Buffer.from(cipher);tampered[tampered.length-1]^=1;
let rejected=false;try{open(tampered,privateKey);}catch{rejected=true;}
if(!rejected)throw Error('Tampered encrypted payload was accepted');
console.log('PASS: encrypted transfer round-trip and tamper rejection.');
