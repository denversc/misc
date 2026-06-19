import { rogersBill } from "./documents/rogers.ts";
import { publicMobileStatement } from "./documents/public_mobile.ts";
import {
  questradeMarginStatement,
  questradeRESPStatement,
  questradeRRSPStatement,
} from "./documents/questrade.ts";

export const allDocuments = Object.freeze([
  publicMobileStatement,
  rogersBill,
  questradeMarginStatement,
  questradeRESPStatement,
  questradeRRSPStatement,
]);

export type Documents = Exclude<(typeof allDocuments)[number], undefined>;
