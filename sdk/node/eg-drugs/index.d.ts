export interface Drug {
  id: number;
  name: string;
  arabic: string;
  active: string | null;
  company: string | null;
  price: string | null;
  oldprice: string | null;
  barcode: string | null;
  barcodeValid: string | null;
  slug: string | null;
  units: string | null;
  description: string | null;
  uses: string | null;
}

export interface Stats {
  totalDrugs: number;
  uniqueCompanies: number;
  uniqueCategories: number;
  uniqueActiveIngredients: number;
  validBarcodes: number;
  priceChanged: number;
}

export interface SearchOptions {
  limit?: number;
  offset?: number;
}

export class EgDrugsClient {
  constructor(options?: { baseUrl?: string; dbPath?: string; jsonPath?: string });
  search(q: string, options?: SearchOptions): Promise<Drug[]>;
  getById(id: number): Promise<Drug | null>;
  getByBarcode(barcode: string): Promise<Drug | null>;
  getGenerics(active: string, options?: SearchOptions): Promise<Drug[]>;
  loadStats(): Promise<Stats>;
}

export function createClient(options?: {
  baseUrl?: string;
  dbPath?: string;
  jsonPath?: string;
}): EgDrugsClient;

export function search(q: string, options?: SearchOptions): Promise<Drug[]>;
export function getById(id: number): Promise<Drug | null>;
export function getByBarcode(barcode: string): Promise<Drug | null>;
export function getGenerics(active: string, options?: SearchOptions): Promise<Drug[]>;
export function loadStats(): Promise<Stats>;
