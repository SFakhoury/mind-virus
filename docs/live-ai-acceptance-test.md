# Paid Live-AI Acceptance Test

This test verifies the complete local model-backed UI before the final video is
recorded. It is separate from the public Render demonstration.

## Cost and safety boundary

- The session is hard-capped at four paid model calls.
- The program displays a confirmation prompt before making a paid request.
- Do not type `RUN` until the cap is displayed and you intend to spend credit.
- The browser displays actual calls, input tokens, output tokens, and estimated
  cost as the session progresses.
- Never show or send the API key in a screenshot or recording.

## Step 1 — Open a clean PowerShell window

If another local town server is running, return to its PowerShell window and
press `Ctrl+C` first. Then open a new PowerShell window and paste:

```powershell
Set-Location "C:\Users\ADMIN\Documents\GitHub\mind-virus"
python -m unittest discover -s tests
```

Continue only if the test suite ends with `OK`.

## Step 2 — Load the API key privately

If `OPENAI_API_KEY` is already configured in this PowerShell session, skip this
step. Otherwise paste the following block, then enter the key into the hidden
prompt:

```powershell
$mindVirusSecureKey = Read-Host "Paste OPENAI_API_KEY" -AsSecureString
$mindVirusKeyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($mindVirusSecureKey)
try {
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($mindVirusKeyPointer)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($mindVirusKeyPointer)
    $mindVirusSecureKey = $null
    $mindVirusKeyPointer = [IntPtr]::Zero
}
```

This sets the key only in the current PowerShell process. Do not put it in a
tracked file, command history, screenshot, chat message, or browser field.

## Step 3 — Start the paid local town

Paste:

```powershell
python -m scripts.run_town_ui --live
```

The terminal must print:

```text
LIVE AI mode can make at most 4 paid API calls.
Type RUN to continue:
```

Type exactly:

```text
RUN
```

The local browser should open at `http://127.0.0.1:8000`.

## Step 4 — Observe the complete model-backed sequence

Do not refresh or press Reset during the test. Wait for the interface to run.
The first paid call produces Bob's structured belief-and-repetition decision.
If Bob stops the propagation chain, up to three grounded follow-up
conversations run automatically.

Wait until one of these occurs:

- the Live model usage panel reaches four calls and the conversations stop; or
- the sequence finishes earlier because no further permitted action remains.

Confirm all of the following:

- [ ] The page says **LIVE AI MODE**.
- [ ] The transcript contains a model-backed Alice-to-Bob decision.
- [ ] Bob's response distinguishes his firsthand bakery knowledge from Alice's
      unverified claim.
- [ ] Later dialogue does not invent inspections, written statements, records,
      announcements, or other evidence that was never provided.
- [ ] The usage panel reports between one and four API calls.
- [ ] Input and output token counts are greater than zero.
- [ ] Estimated cost is greater than `$0.0000` and remains small.
- [ ] No Python connection error or API error appears.
- [ ] Speech bubbles and transcript entries correspond to the same speakers.

## Step 5 — Capture evidence

Take screenshots showing:

1. the town and **LIVE AI MODE** label;
2. the entire conversation transcript;
3. the Live model usage panel; and
4. the PowerShell window after the server is stopped, with no API key visible.

Send the screenshots and copy the transcript text for review. The job ID,
token counts, call count, and estimated cost are safe to share. The API key and
application access token are not.

## Step 6 — Stop and remove the session key

Return to PowerShell and press `Ctrl+C`. Then paste:

```powershell
$env:OPENAI_API_KEY = $null
Remove-Variable mindVirusSecureKey,mindVirusKeyPointer -ErrorAction SilentlyContinue
```

The session output remains locally in `results/town_session_latest.json` and is
ignored by Git. Do not commit raw output until it has been reviewed for secrets
and selected intentionally as a publication artifact.

## Pass condition

The paid acceptance test passes when the model-backed decision and grounded
follow-up dialogue complete without invented evidence or API errors, the usage
panel agrees with the number of calls, the cost remains within the four-call
boundary, and the test evidence contains no credential.
