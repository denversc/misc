import { rogersBill } from "./documents/rogers.ts";
import { publicMobileStatement } from "./documents/public_mobile.ts";
import { kitchenerUtilitiesBill } from "./documents/kitchener_utilities.ts";
import {
  payStubAnnualBonus,
  payStubGSU,
  payStubMeal,
  payStubRegularPay,
  payStubShuttle,
} from "./documents/paystub.ts";
import { pcMastercardStatement } from "./documents/pcmc.ts";
import { morganStanleyRelease } from "./documents/morgan_stanley.ts";
import {
  questradeMarginStatement,
  questradeRESPStatement,
  questradeRRSPStatement,
} from "./documents/questrade.ts";

export const allDocuments = Object.freeze([
  kitchenerUtilitiesBill,
  morganStanleyRelease,
  payStubAnnualBonus,
  payStubGSU,
  payStubMeal,
  payStubRegularPay,
  payStubShuttle,
  pcMastercardStatement,
  publicMobileStatement,
  questradeMarginStatement,
  questradeRESPStatement,
  questradeRRSPStatement,
  rogersBill,
]);

export type Documents = Exclude<(typeof allDocuments)[number], undefined>;
