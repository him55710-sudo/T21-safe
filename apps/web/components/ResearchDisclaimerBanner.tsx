import { DISCLAIMER } from "@/lib/contracts";

export function ResearchDisclaimerBanner() {
  return (
    <div className="research-banner" role="note" aria-label="Research use limitation">
      <span className="research-banner__mark" aria-hidden="true">
        RUO
      </span>
      <strong>Research prototype.</strong>
      <span>{DISCLAIMER.replace("Research prototype; ", "")}</span>
    </div>
  );
}
