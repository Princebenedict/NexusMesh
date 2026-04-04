<<<<<<< HEAD
import { readFileSync } from "fs";
import path from "path";
import {
  TransactionHash,
  TransactionStatus,
  GenLayerClient,
} from "genlayer-js/types";
import { studionet } from "genlayer-js/chains";

const STUDIO_RPC_URL = "https://studio.genlayer.com/api";
const STUDIO_EXPLORER_URL = "https://explorer-studio.genlayer.com";

const safeJson = (value: unknown) =>
  JSON.stringify(
    value,
    (_, currentValue) =>
      typeof currentValue === "bigint" ? currentValue.toString() : currentValue,
    2
  );

/**
 * Reads the contract .py file and returns a clean Uint8Array that GenVM
 * will accept. Handles the three most common causes of invalid_contract:
 *
 *  1. UTF-8 BOM (ef bb bf) prepended by some editors - stripped
 *  2. Windows CRLF line endings (\r\n) - normalized to LF (\n)
 *  3. Any stray non-printable bytes before the runner comment '#' - stripped
 *
 * After stripping, validates that the first byte is '#' (0x23), which
 * GenVM requires for the runner comment check. Throws a clear local error
 * before wasting a deployment transaction if the file is still wrong.
 */
function readContractCode(filePath: string): Uint8Array {
  const raw = readFileSync(filePath);
  let bytes = Array.from(raw);

  if (bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) {
    bytes = bytes.slice(3);
    console.log("  [deploy] Stripped UTF-8 BOM from contract file.");
  }

  const normalized: number[] = [];
  for (let i = 0; i < bytes.length; i++) {
    if (bytes[i] === 0x0d && bytes[i + 1] === 0x0a) {
      normalized.push(0x0a);
      i++;
    } else {
      normalized.push(bytes[i]);
    }
  }

  let start = 0;
  while (start < normalized.length && normalized[start] !== 0x23) {
    start++;
  }
  const clean = normalized.slice(start);

  if (clean.length === 0 || clean[0] !== 0x23) {
    throw new Error(
      `[deploy] Contract file does not start with '#'. ` +
        `GenVM requires the runner comment on line 1. ` +
        `First byte found: 0x${(clean[0] ?? 0).toString(16).padStart(2, "0")}. ` +
        `Fix: ensure line 1 of your .py file is exactly:\n` +
        `  # {"Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0"}`
    );
  }

  const firstNewline = clean.indexOf(0x0a);
  const firstLineBytes = clean.slice(
    0,
    firstNewline === -1 ? clean.length : firstNewline
  );
  const firstLine = Buffer.from(firstLineBytes).toString("utf8");

  if (!firstLine.includes('"Depends"')) {
    throw new Error(
      `[deploy] Line 1 starts with '#' but does not contain a valid runner comment.\n` +
        `Found:    ${firstLine}\n` +
        `Expected: # {"Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0"}`
    );
  }

  console.log(`  [deploy] Contract file validated. First line: ${firstLine}`);
  console.log(`  [deploy] Contract size: ${clean.length} bytes`);

  return new Uint8Array(clean);
}

function getContractAddress(receipt: any): string | undefined {
  return (
    receipt?.data?.contract_address ??
    receipt?.data?.contractAddress ??
    receipt?.txDataDecoded?.contractAddress ??
    receipt?.txDataDecoded?.contract_address
  );
}

export default async function main(client: GenLayerClient<any>) {
  console.log("===============================================");
  console.log("  Deploying NexusMesh to GenLayer StudioNet...");
  console.log("===============================================");

  const activeChainId = client.chain?.id;
  const activeChainName = client.chain?.name ?? "unknown";

  console.log(`  Active network   : ${activeChainName} (${String(activeChainId ?? "n/a")})`);
  console.log(`  Expected network : ${studionet.name} (${studionet.id})`);

  if (activeChainId !== studionet.id) {
    throw new Error(
      `[deploy] Wrong network selected.\n` +
        `  This script is configured for StudioNet only.\n` +
        `  Current chain: ${activeChainName} (${String(activeChainId ?? "n/a")})\n` +
        `  Fix: run 'genlayer network set studionet' or deploy with\n` +
        `  'genlayer deploy --rpc ${STUDIO_RPC_URL}'`
    );
  }

  const filePath = path.resolve(process.cwd(), "contracts/NexusMesh.py");
  console.log(`\n[1/5] Reading contract from: ${filePath}`);
  const contractCode = readContractCode(filePath);

  console.log("\n[2/5] Validating deployment target...");
  console.log(`  StudioNet RPC    : ${STUDIO_RPC_URL}`);

  console.log("\n[3/5] Sending deployment transaction...");
  const deployTransaction = await client.deployContract({
    code: contractCode,
    args: [250],
  });

  console.log(`  Transaction hash: ${String(deployTransaction)}`);

  console.log("\n[4/5] Waiting for transaction to finalize on StudioNet...");
  console.log("  (This can take 30-120 seconds - do not cancel)");

  const receipt = await client.waitForTransactionReceipt({
    hash: deployTransaction as TransactionHash,
    retries: 200,
  });

  console.log("\n[5/5] Checking receipt...");

  const status =
    (receipt as any).statusName ??
    (receipt as any).status_name ??
    (receipt as any).status;

  const executionResult =
    (receipt as any).txExecutionResultName ??
    (receipt as any).tx_execution_result_name ??
    (receipt as any).txExecutionResult;

  console.log(`  Status:           ${String(status)}`);
  console.log(`  Execution Result: ${String(executionResult)}`);

  const isAcceptedStatus =
    status === TransactionStatus.ACCEPTED ||
    status === TransactionStatus.FINALIZED ||
    status === "ACCEPTED" ||
    status === "FINALIZED";

  if (!isAcceptedStatus) {
    console.error("\n  Full receipt:", safeJson(receipt));
    throw new Error(
      `\n[deploy] FAILED - Transaction not accepted by validators.\n` +
        `  Status: ${String(status)}\n` +
        `  This usually means the contract was rejected during consensus.\n` +
        `  Check the GenLayer Studio Explorer for the full execution trace.`
    );
  }

  if (
    executionResult &&
    executionResult !== "SUCCESS" &&
    executionResult !== "FINISHED"
  ) {
    console.error("\n  Full receipt:", safeJson(receipt));
    throw new Error(
      `\n[deploy] FAILED - Contract accepted but execution returned an error.\n` +
        `  Execution Result: ${String(executionResult)}\n` +
        `  This typically indicates a contract-level error (invalid_contract,\n` +
        `  constructor crash, or bad import). Check GenLayer Studio Explorer.`
    );
  }

  const contractAddress = getContractAddress(receipt);

  if (!contractAddress) {
    console.error("\n  Full receipt:", safeJson(receipt));
    throw new Error(
      `\n[deploy] FAILED - Deployment succeeded but no contract address found in receipt.\n` +
        `  Check the explorer manually using your transaction hash: ${String(deployTransaction)}`
    );
  }

  console.log("\n===============================================");
  console.log("  NexusMesh deployed successfully on StudioNet!");
  console.log("===============================================");
  console.log(`  Contract Address : ${contractAddress}`);
  console.log(`  Transaction Hash : ${String(deployTransaction)}`);
  console.log(
    `  Explorer URL     : ${STUDIO_EXPLORER_URL}/contracts/${contractAddress}`
  );
  console.log("===============================================\n");

  return contractAddress;
}
=======
import { readFileSync } from "fs";
import path from "path";
import { GenLayerClient } from "genlayer-js/types";

const FIXED_FRONTEND_CONTRACT = "0x9026f734759602B4D4Fec05497e259B852ebf540";

export default async function main(client: GenLayerClient<any>) {
  console.log("Deploying NexusMesh to GenLayer Bradbury...");
  console.log("Frontend is pinned to fixed contract address:", FIXED_FRONTEND_CONTRACT);
  console.log("If you deploy a new contract, the frontend will still keep using the fixed address above until you intentionally change the code.");

  const filePath = path.resolve(process.cwd(), "contracts/NexusMesh.py");
  const contractCode = new Uint8Array(readFileSync(filePath));

  const deployTransaction = await client.deployContract({
    code: contractCode,
    args: [250],
  });

  console.log("");
  console.log("Deploy transaction sent successfully.");
  console.log("Transaction Hash:", deployTransaction);
  console.log("");
  console.log("Receipt lookup is being skipped because waitForTransactionReceipt()");
  console.log("is failing on getTransactionAllData in your current SDK/network setup.");
  console.log("");
  console.log("Next step:");
  console.log("1. Check the tx hash in Bradbury explorer");
  console.log("2. Confirm whether the deployment succeeded");
  console.log("3. Frontend remains permanently pinned to:", FIXED_FRONTEND_CONTRACT);
  console.log("4. Only change the frontend contract address later if you intentionally want to move away from the fixed contract");

  return deployTransaction;
}





>>>>>>> 1a088c87b907a643f74d1f705e7bf0a880fdc005
