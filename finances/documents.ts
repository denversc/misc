import { rogersBill } from "./rogers.ts";
import { publicMobileStatement } from "./public_mobile.ts";
import {
  questradeMarginStatement,
  questradeRESPStatement,
  questradeRRSPStatement,
} from "./questrade.ts";

export const allDocuments = Object.freeze([
  publicMobileStatement,
  rogersBill,
  questradeMarginStatement,
  questradeRESPStatement,
  questradeRRSPStatement,
]);

export type Documents = Exclude<(typeof allDocuments)[number], undefined>;
