// ======================================================
// System info — show ffmpeg banner on load
// ======================================================

(async function checkSystem() {
    try {
        const res  = await fetch("/system-info");
        const data = await res.json();
        const banner = document.getElementById("ffmpegBanner");
        if (!banner) return;
        if (data.ffmpeg) {
            banner.textContent = "✅ ffmpeg detected — full HD merged downloads enabled.";
            banner.classList.add("ffmpeg-ok");
        } else {
            banner.textContent =
                "⚠️ ffmpeg not found — downloads use the best pre-merged stream (typically 720p). " +
                "Run: winget install --id Gyan.FFmpeg  then restart the server.";
            banner.classList.add("ffmpeg-warn");
        }
        banner.classList.remove("hidden");
    } catch (_) { /* silent */ }
})();


// ======================================================
// Elements
// ======================================================

const analyzeBtn         = document.getElementById("analyzeBtn");
const downloadBtn        = document.getElementById("downloadBtn");
const cancelBtn          = document.getElementById("cancelBtn");
const resetBtn           = document.getElementById("resetBtn");
const batchBtn           = document.getElementById("batchBtn");

const urlBox             = document.getElementById("videoUrls");
const txtFile            = document.getElementById("txtFile");
const currentUrlInput    = document.getElementById("currentUrl");

const loadingCard        = document.getElementById("loadingCard");
const videoCard          = document.getElementById("videoCard");
const downloadCard       = document.getElementById("downloadCard");
const progressCard       = document.getElementById("progressCard");
const statusCard         = document.getElementById("statusCard");
const jobsCard           = document.getElementById("jobsCard");
const jobsList           = document.getElementById("jobsList");
const jobsSummary        = document.getElementById("jobsSummary");

const qualitySelect      = document.getElementById("qualitySelect");

// Video info
const titleEl            = document.getElementById("videoTitle");
const uploaderEl         = document.getElementById("videoUploader");
const durationEl         = document.getElementById("videoDuration");
const thumbnailEl        = document.getElementById("thumbnail");
const codecsEl           = document.getElementById("videoCodecs");

// Progress
const progressFill       = document.getElementById("progressFill");
const progressPercent    = document.getElementById("progressPercent");
const progressTitle      = document.getElementById("progressTitle");
const progressFilename   = document.getElementById("progressFilename");
const downloadSpeed      = document.getElementById("downloadSpeed");
const downloadEta        = document.getElementById("downloadEta");
const statusMessage      = document.getElementById("statusMessage");


// ======================================================
// State
// ======================================================

let currentJob     = null;
let pollTimer      = null;
let batchPollTimer = null;
let batchJobIds    = [];


// ======================================================
// Helpers
// ======================================================

function getUrls() {
    return urlBox.value
        .split("\n")
        .map(x => x.trim())
        .filter(x => x);
}

/**
 * Show a status message with a colour class.
 * type: "ok" | "err" | "warn" | "info"
 */
function showStatus(message, type = "info") {
    statusCard.classList.remove("hidden");
    statusMessage.className = `status-${type}`;
    statusMessage.innerText = message;
}

function hideStatus() {
    statusCard.classList.add("hidden");
}

function resetProgress() {
    progressFill.style.width = "0%";
    progressFill.classList.remove("complete");
    progressPercent.innerText = "0%";
    downloadSpeed.innerText = "--";
    downloadEta.innerText = "--";
    if (progressTitle)   progressTitle.innerText = "Download Progress";
    if (progressFilename) progressFilename.classList.add("hidden");
}

function setLoading(show) {
    if (!loadingCard) return;
    loadingCard.classList.toggle("hidden", !show);
}

function fmtSeconds(sec) {
    if (!sec) return "--";
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    if (h) return `${h}h ${m}m ${s}s`;
    if (m) return `${m}m ${s}s`;
    return `${s}s`;
}

/** Trim a URL to a readable label for the queue */
function shortUrl(url) {
    try {
        const u = new URL(url);
        const v = u.searchParams.get("v");
        return v ? `youtube.com/watch?v=${v}` : (u.hostname + u.pathname).slice(0, 55);
    } catch (_) {
        return url.slice(0, 55);
    }
}


// ======================================================
// TXT Upload — append URLs to textarea
// ======================================================

if (txtFile) {
    txtFile.addEventListener("change", () => {
        const file = txtFile.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function (e) {
            const incoming = e.target.result.trim();
            const existing = urlBox.value.trim();
            urlBox.value = existing ? existing + "\n" + incoming : incoming;
        };
        reader.readAsText(file);
    });
}


// ======================================================
// Reset single-URL flow ("Download Another" button)
// ======================================================

function resetSingleFlow() {
    // Stop any running poll
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    currentJob = null;

    // Hide all single-URL result cards
    videoCard.classList.add("hidden");
    downloadCard.classList.add("hidden");
    progressCard.classList.add("hidden");
    hideStatus();

    // Reset buttons
    analyzeBtn.disabled  = false;
    downloadBtn.disabled = false;
    downloadBtn.innerText = "⬇ Download This Video";
    cancelBtn.classList.add("hidden");
    resetBtn.classList.add("hidden");

    resetProgress();
}

if (resetBtn) {
    resetBtn.addEventListener("click", resetSingleFlow);
}


// ======================================================
// Analyze (single URL)
// ======================================================

analyzeBtn.addEventListener("click", async () => {

    const urls = getUrls();
    if (urls.length === 0) {
        alert("Enter at least one YouTube URL.");
        return;
    }

    const url = urls[0];

    analyzeBtn.disabled  = true;
    analyzeBtn.innerText = "Analyzing…";
    setLoading(true);

    // Hide stale results from a previous run
    videoCard.classList.add("hidden");
    downloadCard.classList.add("hidden");
    progressCard.classList.add("hidden");
    hideStatus();

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: "Analyze failed" }));
            throw new Error(err.detail || "Analyze failed");
        }

        const data = await response.json();

        currentUrlInput.value = url;

        titleEl.innerText    = data.title    || "Unknown";
        uploaderEl.innerText = data.uploader || "Unknown";
        durationEl.innerText = fmtSeconds(data.duration);
        thumbnailEl.src      = data.thumbnail || "";
        codecsEl.innerText   = (data.codecs && data.codecs.length)
            ? data.codecs.join(", ") : "—";

        qualitySelect.innerHTML = "";
        (data.options || []).forEach(option => {
            const opt = document.createElement("option");
            opt.value = option.value;
            opt.textContent = option.label;
            qualitySelect.appendChild(opt);
        });

        videoCard.classList.remove("hidden");
        downloadCard.classList.remove("hidden");
        // Make sure download button is fresh
        downloadBtn.disabled  = false;
        downloadBtn.innerText = "⬇ Download This Video";
        cancelBtn.classList.add("hidden");
        resetBtn.classList.add("hidden");

    } catch (err) {
        showStatus("❌ " + err.message, "err");
    } finally {
        setLoading(false);
        analyzeBtn.disabled  = false;
        analyzeBtn.innerText = "Analyze & Choose Quality";
    }

});


// ======================================================
// Download (single URL)
// ======================================================

downloadBtn.addEventListener("click", async () => {

    const url = currentUrlInput.value;
    if (!url) {
        alert("Please analyze a URL first.");
        return;
    }

    downloadBtn.disabled  = true;
    analyzeBtn.disabled   = true;
    downloadBtn.innerText = "Downloading…";
    cancelBtn.classList.remove("hidden");
    resetBtn.classList.add("hidden");

    resetProgress();
    progressCard.classList.remove("hidden");
    showStatus("Starting download…", "info");

    try {

        const response = await fetch("/download", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, format_id: qualitySelect.value }),
        });

        if (!response.ok) throw new Error("Download request failed");

        const data  = await response.json();
        currentJob  = data.job_id;
        pollProgress();

    } catch (err) {
        showStatus("❌ " + err.message, "err");
        downloadBtn.disabled  = false;
        analyzeBtn.disabled   = false;
        downloadBtn.innerText = "⬇ Download This Video";
        cancelBtn.classList.add("hidden");
    }

});


// ======================================================
// Cancel (single URL)
// ======================================================

if (cancelBtn) {
    cancelBtn.addEventListener("click", async () => {
        if (currentJob) {
            await fetch("/cancel/" + currentJob, { method: "POST" }).catch(() => {});
        }
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }

        showStatus("⛔ Download cancelled.", "warn");
        downloadBtn.disabled  = false;
        analyzeBtn.disabled   = false;
        downloadBtn.innerText = "⬇ Download This Video";
        cancelBtn.classList.add("hidden");
        resetBtn.classList.remove("hidden");
    });
}


// ======================================================
// Progress Polling (single URL)
// ======================================================

function pollProgress() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = setInterval(loadProgress, 1000);
}

async function loadProgress() {
    if (!currentJob) return;

    try {

        const response = await fetch("/progress/" + currentJob);
        const data     = await response.json();

        const pct = Math.min(100, data.progress || 0);
        progressFill.style.width    = pct + "%";
        progressPercent.innerText   = pct.toFixed(1) + "%";
        downloadSpeed.innerText     = data.speed || "--";
        downloadEta.innerText       = fmtSeconds(data.eta);

        if (data.status === "downloading") {
            showStatus("Downloading… " + pct.toFixed(1) + "%", "info");
        }

        if (data.status === "completed") {
            clearInterval(pollTimer); pollTimer = null;

            progressFill.style.width    = "100%";
            progressPercent.innerText   = "100%";
            progressFill.classList.add("complete");
            if (progressTitle) progressTitle.innerText = "✅ Download Complete";

            if (data.filename && progressFilename) {
                progressFilename.innerText = "📁 " + data.filename;
                progressFilename.classList.remove("hidden");
            }

            downloadSpeed.innerText = "--";
            downloadEta.innerText   = "--";

            showStatus("✅ Download completed — " + (data.filename || ""), "ok");

            downloadBtn.disabled  = false;
            analyzeBtn.disabled   = false;
            downloadBtn.innerText = "⬇ Download This Video";
            cancelBtn.classList.add("hidden");
            resetBtn.classList.remove("hidden");
        }

        if (data.status === "failed") {
            clearInterval(pollTimer); pollTimer = null;
            showStatus("❌ Download failed — " + data.error, "err");
            downloadBtn.disabled  = false;
            analyzeBtn.disabled   = false;
            downloadBtn.innerText = "⬇ Download This Video";
            cancelBtn.classList.add("hidden");
            resetBtn.classList.remove("hidden");
        }

        if (data.status === "cancelled") {
            clearInterval(pollTimer); pollTimer = null;
            showStatus("⛔ Download cancelled.", "warn");
            downloadBtn.disabled  = false;
            analyzeBtn.disabled   = false;
            downloadBtn.innerText = "⬇ Download This Video";
            cancelBtn.classList.add("hidden");
            resetBtn.classList.remove("hidden");
        }

    } catch (err) {
        console.log("Progress error:", err);
    }
}


// ======================================================
// Batch Download
// ======================================================

batchBtn.addEventListener("click", async () => {

    const urls = getUrls();
    if (urls.length === 0) {
        alert("Enter at least one YouTube URL.");
        return;
    }

    batchBtn.disabled  = true;
    batchBtn.innerText = "Queuing…";

    try {

        const response = await fetch("/batch-download", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ urls, format_id: "best" }),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: "Batch request failed" }));
            throw new Error(err.detail || "Batch request failed");
        }

        const data   = await response.json();
        batchJobIds  = data.jobs.map(j => j.job_id);

        // Seed the queue display immediately with "queued" rows
        renderJobsTable(
            batchJobIds.map((id, i) => ({
                id,
                status:   "queued",
                progress: 0,
                filename: "",
                _url:     urls[i] || "",
            }))
        );

        jobsCard.classList.remove("hidden");
        // Scroll to the queue
        jobsCard.scrollIntoView({ behavior: "smooth", block: "start" });

        if (batchPollTimer) clearInterval(batchPollTimer);
        batchPollTimer = setInterval(refreshJobs, 1500);

    } catch (err) {
        alert("Batch error: " + err.message);
    } finally {
        batchBtn.disabled  = false;
        batchBtn.innerText = "Download All (Best Quality)";
    }

});


// ======================================================
// Batch Jobs Polling
// ======================================================

// Map of job_id → original URL (kept for label before filename is known)
const jobUrlMap = {};

async function refreshJobs() {
    try {
        const response = await fetch("/jobs");
        const allJobs  = await response.json();

        const relevant = batchJobIds.length
            ? allJobs.filter(j => batchJobIds.includes(j.id))
            : allJobs;

        renderJobsTable(relevant);

        const done  = relevant.filter(j => !["queued","downloading"].includes(j.status));
        const total = relevant.length;
        if (jobsSummary) {
            jobsSummary.textContent = total
                ? `${done.length} / ${total} done`
                : "";
        }

        // Stop when all finished
        const active = relevant.filter(j => ["queued","downloading"].includes(j.status));
        if (active.length === 0 && relevant.length > 0) {
            clearInterval(batchPollTimer);
            if (jobsSummary) jobsSummary.textContent = `✅ All ${total} downloads finished`;
        }

    } catch (err) {
        console.log("Jobs poll error:", err);
    }
}


function renderJobsTable(jobs) {

    if (!jobs || jobs.length === 0) {
        jobsList.innerHTML = `<p style="color:#666;font-size:13px;">No jobs yet…</p>`;
        return;
    }

    jobsList.innerHTML = jobs.map((job, i) => {

        const label = job.filename
            ? job.filename
            : (jobUrlMap[job.id] || shortUrl(job._url || job.id));

        const barHtml = (job.status === "downloading")
            ? `<div class="job-bar">
                 <div class="job-bar-fill" style="width:${job.progress}%"></div>
               </div>`
            : "";

        return `<div class="job-row">
            <div style="flex:1;min-width:0;">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
                    <span class="job-name">${i + 1}. ${label}</span>
                    <span class="job-status ${job.status}">${job.status}</span>
                </div>
                ${barHtml}
            </div>
        </div>`;

    }).join("");
}


// ======================================================
// Playlist — Elements
// ======================================================

const playlistUrlInput       = document.getElementById("playlistUrl");
const playlistAnalyzeBtn     = document.getElementById("playlistAnalyzeBtn");
const playlistDownloadBtn    = document.getElementById("playlistDownloadBtn");
const playlistLoadingCard    = document.getElementById("playlistLoadingCard");
const playlistInfoCard       = document.getElementById("playlistInfoCard");
const playlistTitleEl        = document.getElementById("playlistTitle");
const playlistMetaEl         = document.getElementById("playlistMeta");
const playlistEntriesEl      = document.getElementById("playlistEntries");
const playlistProgressCard   = document.getElementById("playlistProgressCard");
const playlistProgressTitle  = document.getElementById("playlistProgressTitle");
const playlistProgressFill   = document.getElementById("playlistProgressFill");
const playlistProgressPct    = document.getElementById("playlistProgressPercent");
const playlistProgressCount  = document.getElementById("playlistProgressCount");
const playlistSpeedEl        = document.getElementById("playlistSpeed");
const playlistCurrentFile    = document.getElementById("playlistCurrentFile");
const playlistStatusCard     = document.getElementById("playlistStatusCard");
const playlistStatusMsg      = document.getElementById("playlistStatusMsg");


// ======================================================
// Playlist — State
// ======================================================

let playlistJobId   = null;
let playlistTotal   = 0;
let playlistTimer   = null;


// ======================================================
// Playlist — Helpers
// ======================================================

function showPlaylistStatus(msg, type = "info") {
    playlistStatusCard.classList.remove("hidden");
    playlistStatusMsg.className = `status-${type}`;
    playlistStatusMsg.innerText = msg;
}

function hidePlaylistStatus() {
    playlistStatusCard.classList.add("hidden");
}


// ======================================================
// Playlist — Preview (analyze)
// ======================================================

playlistAnalyzeBtn.addEventListener("click", async () => {

    const url = playlistUrlInput.value.trim();
    if (!url) {
        alert("Enter a playlist URL.");
        return;
    }

    playlistAnalyzeBtn.disabled  = true;
    playlistAnalyzeBtn.innerText = "Fetching…";
    playlistLoadingCard.classList.remove("hidden");
    playlistInfoCard.classList.add("hidden");
    playlistDownloadBtn.classList.add("hidden");
    hidePlaylistStatus();

    try {

        const res = await fetch("/analyze-playlist", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: "Failed" }));
            throw new Error(err.detail || "Failed to fetch playlist");
        }

        const data = await res.json();
        playlistTotal = data.count;

        // Header
        playlistTitleEl.innerText = data.title || "Playlist";
        playlistMetaEl.textContent =
            `${data.count} video${data.count !== 1 ? "s" : ""}` +
            (data.uploader ? ` · ${data.uploader}` : "");

        // Video list
        playlistEntriesEl.innerHTML = data.entries.map(e => {
            const dur = e.duration ? fmtSeconds(e.duration) : "--";
            return `<div class="job-row">
                <span class="job-name">${e.index}. ${e.title}</span>
                <span style="color:#666;font-size:12px;white-space:nowrap;margin-left:10px;">${dur}</span>
            </div>`;
        }).join("");

        playlistInfoCard.classList.remove("hidden");
        playlistDownloadBtn.classList.remove("hidden");

    } catch (err) {
        showPlaylistStatus("❌ " + err.message, "err");
    } finally {
        playlistLoadingCard.classList.add("hidden");
        playlistAnalyzeBtn.disabled  = false;
        playlistAnalyzeBtn.innerText = "Preview Playlist";
    }

});


// ======================================================
// Playlist — Download
// ======================================================

playlistDownloadBtn.addEventListener("click", async () => {

    const url = playlistUrlInput.value.trim();
    if (!url) return;

    playlistDownloadBtn.disabled  = true;
    playlistDownloadBtn.innerText = "Starting…";
    playlistAnalyzeBtn.disabled   = true;

    // Reset & show progress card
    playlistProgressFill.style.width   = "0%";
    playlistProgressFill.classList.remove("complete");
    playlistProgressPct.innerText      = "0%";
    playlistProgressCount.innerText    = `0 / ${playlistTotal}`;
    playlistSpeedEl.innerText          = "--";
    playlistProgressTitle.innerText    = "Playlist Download Progress";
    if (playlistCurrentFile) playlistCurrentFile.classList.add("hidden");

    playlistProgressCard.classList.remove("hidden");
    showPlaylistStatus("Starting playlist download…", "info");

    try {

        const res = await fetch("/download-playlist", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, format_id: "best" }),
        });

        if (!res.ok) throw new Error("Download request failed");

        const data     = await res.json();
        playlistJobId  = data.job_id;

        showPlaylistStatus("Downloading playlist…", "info");
        startPlaylistPoll();

    } catch (err) {
        showPlaylistStatus("❌ " + err.message, "err");
        playlistDownloadBtn.disabled  = false;
        playlistAnalyzeBtn.disabled   = false;
        playlistDownloadBtn.innerText = "⬇ Download Entire Playlist";
    }

});


// ======================================================
// Playlist — Progress polling
// ======================================================

function startPlaylistPoll() {
    if (playlistTimer) clearInterval(playlistTimer);
    playlistTimer = setInterval(pollPlaylistProgress, 1500);
}

async function pollPlaylistProgress() {
    if (!playlistJobId) return;

    try {

        const res  = await fetch("/progress/" + playlistJobId);
        const data = await res.json();

        // Overall progress bar
        const pct = Math.min(100, data.progress || 0);
        playlistProgressFill.style.width = pct + "%";
        playlistProgressPct.innerText    = pct.toFixed(1) + "%";
        playlistSpeedEl.innerText        = data.speed || "--";

        // Show current file being downloaded
        if (data.filename && playlistCurrentFile) {
            playlistCurrentFile.innerText = "▶ " + data.filename;
            playlistCurrentFile.classList.remove("hidden");
        }

        // Exact video counter from server
        const done  = data.completed_count || 0;
        const total = data.total || playlistTotal;
        if (total > 0) {
            playlistProgressCount.innerText = `${done} / ${total}`;
        }

        if (data.status === "completed") {
            clearInterval(playlistTimer); playlistTimer = null;

            playlistProgressFill.style.width = "100%";
            playlistProgressFill.classList.add("complete");
            playlistProgressPct.innerText    = "100%";
            playlistProgressCount.innerText  = `${playlistTotal} / ${playlistTotal}`;
            playlistProgressTitle.innerText  = "✅ Playlist Downloaded";

            if (playlistCurrentFile) {
                playlistCurrentFile.innerText = "📁 Saved to: " + (data.filename || "");
                playlistCurrentFile.classList.remove("hidden");
            }

            showPlaylistStatus(
                `✅ Playlist downloaded — ${data.filename || ""}`, "ok"
            );

            playlistDownloadBtn.disabled  = false;
            playlistAnalyzeBtn.disabled   = false;
            playlistDownloadBtn.innerText = "⬇ Download Entire Playlist";
        }

        if (data.status === "failed") {
            clearInterval(playlistTimer); playlistTimer = null;
            showPlaylistStatus("❌ Download failed — " + data.error, "err");
            playlistDownloadBtn.disabled  = false;
            playlistAnalyzeBtn.disabled   = false;
            playlistDownloadBtn.innerText = "⬇ Download Entire Playlist";
        }

    } catch (err) {
        console.log("Playlist poll error:", err);
    }
}
