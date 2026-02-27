export const DATASET_TO_GEO_COUNTRY: Record<string, string> = {
  USA: "United States of America",
  UK: "United Kingdom"
};

export const GEO_TO_DATASET_COUNTRY: Record<string, string> = Object.fromEntries(
  Object.entries(DATASET_TO_GEO_COUNTRY).map(([k, v]) => [v, k])
);

