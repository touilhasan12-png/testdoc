import React, {createContext, useContext} from 'react';
import {Cam} from './core';

export type StageState = {frame: number; cam: Cam; shotId: string};
export const StageCtx = createContext<StageState | null>(null);
export const useStage = (): StageState => {
  const v = useContext(StageCtx);
  if (!v) throw new Error('no stage');
  return v;
};
