/* ==========================================
   SOURCE FILTER
========================================== */

let currentSource = "ALL";
let newsTrendChart = null;

function sourceQuery() {
    return `?source=${encodeURIComponent(currentSource)}`;
}


/* ==========================================
   LOAD SUMMARY
========================================== */

async function loadSummary() {

    try {

        const response = await fetch(
            `/api/summary${sourceQuery()}`
        );

        if (!response.ok) {
            throw new Error("Gagal mengambil summary");
        }

        const data = await response.json();

        document.getElementById(
            "totalArticles"
        ).textContent = data.total_articles;

        document.getElementById(
            "totalInvestment"
        ).textContent = data.total_investment;

        document.getElementById(
            "totalCapacity"
        ).textContent = data.total_capacity;

        document.getElementById(
            "totalTechnology"
        ).textContent = data.total_technology;

    }

    catch (error) {

        console.error(
            "Summary error:",
            error
        );

    }

}


/* ==========================================
   LOAD NEWS TREND
========================================== */

async function loadNewsTrend() {

    try {

        const response = await fetch(
            `/api/trends${sourceQuery()}`
        );

        if (!response.ok) {
            throw new Error(
                "Gagal mengambil data trend"
            );
        }

        const data = await response.json();

        // Trend Insight
        const trendInsight =
            document.getElementById(
                "trendInsight"
            );

        if (trendInsight && data.length > 0) {

            const highestWeek =
                data.reduce(
                    (max, item) =>
                        item.total > max.total
                            ? item
                            : max,
                    data[0]
                );

            const highestIndex =
                data.findIndex(
                    item =>
                        item.week === highestWeek.week
                );

            let insightText =
                `Minggu dengan jumlah pemberitaan tertinggi adalah ` +
                `<strong>${highestWeek.week}</strong> ` +
                `dengan <strong>${highestWeek.total} artikel</strong>.`;

            if (highestIndex > 0) {

                const previousWeek =
                    data[highestIndex - 1];

                const difference =
                    highestWeek.total -
                    previousWeek.total;

                if (difference > 0) {

                    insightText +=
                        ` Jumlah tersebut meningkat ` +
                        `<strong>${difference} artikel</strong> ` +
                        `dibandingkan minggu sebelumnya ` +
                        `(${previousWeek.week}).`;

                }

                else if (difference < 0) {

                    insightText +=
                        ` Jumlah tersebut menurun ` +
                        `<strong>${Math.abs(difference)} artikel</strong> ` +
                        `dibandingkan minggu sebelumnya ` +
                        `(${previousWeek.week}).`;

                }

                else {

                    insightText +=
                        ` Jumlah tersebut sama dengan ` +
                        `minggu sebelumnya.`;

                }

            }

            trendInsight.innerHTML =
                `<strong>Trend Insight:</strong> ${insightText}`;

        }

        else if (trendInsight) {

            trendInsight.textContent =
                "Belum tersedia data trend.";

        }

        const labels = data.map(
            item => item.week
        );

        const values = data.map(
            item => item.total
        );

        const canvas = document.getElementById(
            "newsTrendChart"
        );

        if (newsTrendChart) {
            newsTrendChart.destroy();
        }

        newsTrendChart = new Chart(canvas, {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {

                        label: "Jumlah Artikel",

                        data: values,

                        borderWidth: 3,

                        tension: 0.3,

                        pointRadius: 4,

                        pointHoverRadius: 6,

                        fill: false

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        display: true

                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {

                            precision: 0

                        }

                    }

                }

            }

        });

    }

    catch (error) {

        console.error(
            "Trend error:",
            error
        );

    }

}


/* ==========================================
   CREATE DATA ROW
========================================== */

function createDataRow(
    name,
    count
) {

    const row = document.createElement(
        "div"
    );

    row.className = "data-row";


    const nameElement =
        document.createElement("span");

    nameElement.className =
        "data-name";

    nameElement.textContent = name;


    const countElement =
        document.createElement("span");

    countElement.className =
        "data-count";

    countElement.textContent =
        `${count} artikel`;


    row.appendChild(
        nameElement
    );

    row.appendChild(
        countElement
    );


    return row;

}


/* ==========================================
   CREATE SIGNAL
========================================== */

function createSignal(value) {

    const element = document.createElement("div");
    element.className = "signal";

    const label = document.createElement("span");
    const badge = document.createElement("span");

    if (typeof value === "object" && value !== null) {

        label.textContent =
            value.range || value.name || "-";

        badge.textContent =
            `${value.count || 0} artikel`;

    } else {

        label.textContent = value;
        badge.textContent = "0 artikel";

    }

    badge.className = "signal-count";

    element.appendChild(label);
    element.appendChild(badge);

    return element;
}

/* ==========================================
   LOAD BUSINESS INSIGHTS
========================================== */

async function loadInsights() {

    try {

        const response = await fetch(
            `/api/insights${sourceQuery()}`
        );

        if (!response.ok) {

            throw new Error(
                "Gagal mengambil business insights"
            );

        }

        const data = await response.json();


        /* ==========================================
           BUSINESS INSIGHT INTERPRETATION
        ========================================== */

        const summary = data.summary;

        const totalArticles =
            data.total_articles || 0;

        function calculatePercentage(count, total) {

            if (!total || total === 0) {
                return "0%";
            }

            return `${(
                (count / total) * 100
            ).toFixed(1)}%`;

}

        /* ==================================
           TOP TOPIC
        ================================== */

        document.getElementById(
            "topTopic"
        ).textContent =
            summary.top_topic || "-";

        const topicPercentage =
            calculatePercentage(
                summary.top_topic_count || 0,
                totalArticles
            );

        document.getElementById(
            "topTopicDescription"
        ).textContent =
            `${summary.top_topic_count || 0} dari ${totalArticles} artikel ` +
            `(${topicPercentage}) membahas topik ${summary.top_topic || "-"}. ` +
            `Data ini menunjukkan bahwa topik tersebut menjadi salah satu fokus utama ` +
            `dalam pemberitaan yang sedang dianalisis.`;


        /* ==================================
           TOP TECHNOLOGY
        ================================== */

        document.getElementById(
            "topTechnology"
        ).textContent =
            summary.top_technology || "-";

        const technologyPercentage =
            calculatePercentage(
                summary.top_technology_count || 0,
                totalArticles
            );

        document.getElementById(
            "topTechnologyDescription"
        ).textContent =
            `${summary.top_technology_count || 0} dari ${totalArticles} artikel ` +
            `(${technologyPercentage}) menyebut ${summary.top_technology || "-"}. ` +
            `Informasi ini dapat digunakan untuk melihat teknologi yang paling sering ` +
            `muncul dalam pemberitaan.`;


        /* ==================================
           TOP LOCATION
        ================================== */

        document.getElementById(
            "topLocation"
        ).textContent =
            summary.top_location || "-";

        const locationPercentage =
            calculatePercentage(
                summary.top_location_count || 0,
                totalArticles
            );

        document.getElementById(
            "topLocationDescription"
        ).textContent =
            `${summary.top_location_count || 0} dari ${totalArticles} artikel ` +
            `(${locationPercentage}) menyebut ${summary.top_location || "-"}. ` +
            `Lokasi tersebut menjadi salah satu wilayah yang paling sering muncul ` +
            `dalam data pemberitaan.`;


        /* ==================================
           TOP COMPANY
        ================================== */

        document.getElementById(
            "topCompany"
        ).textContent =
            summary.top_company || "-";

        const companyPercentage =
            calculatePercentage(
                summary.top_company_count || 0,
                totalArticles
            );

        document.getElementById(
            "topCompanyDescription"
        ).textContent =
            `${summary.top_company_count || 0} dari ${totalArticles} artikel ` +
            `(${companyPercentage}) menyebut ${summary.top_company || "-"}. ` +
            `Data ini menunjukkan bahwa perusahaan tersebut cukup sering muncul ` +
            `dalam pemberitaan yang dianalisis.`;


        /* ==================================
           TOPICS
        ================================== */

        const topicsList =
            document.getElementById(
                "topicsList"
            );

        topicsList.innerHTML = "";

        if (!data.topics || data.topics.length === 0) {

            topicsList.innerHTML =
                `<div class="loading">
                    Tidak ada data.
                </div>`;

        }

        else {

            data.topics.forEach(
                item => {

                    topicsList.appendChild(
                        createDataRow(
                            item.name,
                            item.count
                        )
                    );

                }
            );

        }


        /* ==================================
           TECHNOLOGIES
        ================================== */

        const technologyList =
            document.getElementById(
                "technologyList"
            );

        technologyList.innerHTML = "";

        if (
            !data.technologies ||
            data.technologies.length === 0
        ) {

            technologyList.innerHTML =
                `<div class="loading">
                    Tidak ada data.
                </div>`;

        }

        else {

            data.technologies.forEach(
                item => {

                    technologyList.appendChild(
                        createDataRow(
                            item.name,
                            item.count
                        )
                    );

                }
            );

        }


        /* ==================================
            INVESTMENTS
        ================================== */

        const investmentList =
            document.getElementById("investmentList");

        investmentList.innerHTML = "";

        if (
            !data.investments ||
            data.investments.length === 0
        ) {
            investmentList.textContent =
                "Tidak ada data investasi.";
        } else {

            data.investments.forEach(item => {

                const row =
                    document.createElement("div");

                row.className = "data-row";

                const name =
                    document.createElement("span");

                name.className = "data-name";

                name.textContent =
                    item.range;

                const count =
                    document.createElement("span");

                count.className = "data-count";

                count.textContent =
                    `${item.count} artikel`;

                row.appendChild(name);
                row.appendChild(count);

                investmentList.appendChild(row);
            });
        }


        /* ==================================
        CAPACITIES
        ================================= */

        const capacityList =
            document.getElementById("capacityList");

        capacityList.innerHTML = "";

        if (
            !data.capacities ||
            data.capacities.length === 0
        ) {

            capacityList.textContent =
                "Tidak ada data kapasitas.";

        } else {

            data.capacities.forEach(item => {

                const row =
                    document.createElement("div");

                row.className = "data-row";

                const name =
                    document.createElement("span");

                name.className = "data-name";

                name.textContent =
                    item.range;

                const count =
                    document.createElement("span");

                count.className = "data-count";

                count.textContent =
                    `${item.count} artikel`;

                row.appendChild(name);
                row.appendChild(count);

                capacityList.appendChild(row);

            });
        }


        /* ==================================
           COMPANIES
        ================================== */

        const companyList =
            document.getElementById(
                "companyList"
            );

        companyList.innerHTML = "";

        if (
            !data.companies ||
            data.companies.length === 0
        ) {

            companyList.innerHTML =
                `<div class="loading">
                    Tidak ada data.
                </div>`;

        }

        else {

            data.companies.forEach(
                item => {

                    companyList.appendChild(
                        createDataRow(
                            item.name,
                            item.count
                        )
                    );

                }
            );

        }


        /* ==================================
           ORGANIZATIONS
        ================================== */

        const organizationList =
            document.getElementById(
                "organizationList"
            );

        organizationList.innerHTML = "";

        if (
            !data.organizations ||
            data.organizations.length === 0
        ) {

            organizationList.innerHTML =
                `<div class="loading">
                    Tidak ada data.
                </div>`;

        }

        else {

            data.organizations.forEach(
                item => {

                    organizationList.appendChild(
                        createDataRow(
                            item.name,
                            item.count
                        )
                    );

                }
            );

        }


        /* ==================================
           LOCATIONS
        ================================== */

        const locationList =
            document.getElementById(
                "locationList"
            );

        locationList.innerHTML = "";

        if (
            !data.locations ||
            data.locations.length === 0
        ) {

            locationList.innerHTML =
                `<div class="loading">
                    Tidak ada data.
                </div>`;

        }

        else {

            data.locations.forEach(
                item => {

                    locationList.appendChild(
                        createDataRow(
                            item.name,
                            item.count
                        )
                    );

                }
            );

        }

    }

    catch (error) {

        console.error(
            "Insight error:",
            error
        );

        const topicsList =
            document.getElementById(
                "topicsList"
            );

        if (topicsList) {

            topicsList.innerHTML = `
                <div class="loading">
                    Gagal memuat business insight.
                </div>
            `;

        }

    }

}


/* ==========================================
   FORMAT DATE
========================================== */

function formatDate(dateString) {

    if (!dateString) {
        return "";
    }

    const date =
        new Date(dateString);

    return date.toLocaleDateString(
        "id-ID",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );

}


/* ==========================================
   CREATE NEWS INSIGHT TAGS
========================================== */

function createNewsInsightTags(news) {

    const tags = [];


    if (news.technology) {

        tags.push(
            `Technology: ${news.technology}`
        );

    }


    if (news.investment_value) {

        tags.push(
            `Investment: ${news.investment_value}`
        );

    }


    if (news.capacity) {

        tags.push(
            `Capacity: ${news.capacity}`
        );

    }


    if (news.company) {

        tags.push(
            `Company: ${news.company}`
        );

    }


    if (news.project_location) {

        tags.push(
            `Location: ${news.project_location}`
        );

    }


    if (news.organization) {

        tags.push(
            `Organization: ${news.organization}`
        );

    }


    return tags;

}


/* ==========================================
   LOAD NEWS
========================================== */

async function loadNews() {

    const container =
        document.getElementById(
            "newsContainer"
        );

    try {

        const response = await fetch(
            `/api/news${sourceQuery()}`
        );

        if (!response.ok) {

            throw new Error(
                "Gagal mengambil berita"
            );

        }

        const newsList =
            await response.json();

        container.innerHTML = "";


        if (newsList.length === 0) {

            container.innerHTML = `
                <div class="loading">
                    Tidak ada berita untuk sumber ini.
                </div>
            `;

            return;

        }


        newsList.forEach(
            news => {

                const card =
                    document.createElement(
                        "article"
                    );

                card.className =
                    "news-card";


                /* ==========================
                   IMAGE
                ========================== */

                const image =
                    document.createElement(
                        "img"
                    );

                image.className =
                    "news-image";

                image.alt =
                    news.title;


                if (news.image_url) {

                    image.src =
                        news.image_url;

                }

                else {

                    image.src =
                        "https://via.placeholder.com/800x450?text=Data+Center";

                }


                /* ==========================
                   BODY
                ========================== */

                const body =
                    document.createElement(
                        "div"
                    );

                body.className =
                    "news-body";


                /* ==========================
                   META
                ========================== */

                const meta =
                    document.createElement(
                        "div"
                    );

                meta.className =
                    "news-meta";


                const date =
                    document.createElement(
                        "span"
                    );

                date.className =
                    "date";

                date.textContent =
                    formatDate(
                        news.published_date
                    );

                meta.appendChild(
                    date
                );


                /* SOURCE */

                if (news.source) {

                    const sourceTag =
                        document.createElement(
                            "span"
                        );

                    sourceTag.className =
                        "tag";

                    sourceTag.textContent =
                        news.source;

                    meta.appendChild(
                        sourceTag
                    );

                }


                /* TOPIC */

                if (news.topic) {

                    const tag =
                        document.createElement(
                            "span"
                        );

                    tag.className =
                        "tag";

                    tag.textContent =
                        news.topic;

                    meta.appendChild(
                        tag
                    );

                }


                /* ==========================
                   TITLE
                ========================== */

                const title =
                    document.createElement(
                        "h3"
                    );

                title.className =
                    "news-title";

                title.textContent =
                    news.title;


                /* ==========================
                   SUMMARY
                ========================== */

                const summary =
                    document.createElement(
                        "p"
                    );

                summary.className =
                    "news-summary";

                summary.textContent =
                    news.summary ||
                    (
                        news.content
                            ? news.content.substring(0, 250) + "..."
                            : "Tidak ada ringkasan tersedia."
                    );


                /* ==========================
                   BUSINESS INSIGHT
                ========================== */

                const insight =
                    document.createElement(
                        "div"
                    );

                insight.className =
                    "business-insight";


                const insightTitle =
                    document.createElement(
                        "div"
                    );

                insightTitle.className =
                    "business-insight-title";

                insightTitle.textContent =
                    "EXTRACTED INFORMATION";


                const insightTags =
                    document.createElement(
                        "div"
                    );

                insightTags.className =
                    "insight-tags";


                const tags =
                    createNewsInsightTags(
                        news
                    );


                if (tags.length === 0) {

                    const empty =
                        document.createElement(
                            "span"
                        );

                    empty.className =
                        "insight-tag";

                    empty.textContent =
                        "Belum ada informasi tambahan";

                    insightTags.appendChild(
                        empty
                    );

                }

                else {

                    tags.forEach(
                        tag => {

                            const element =
                                document.createElement(
                                    "span"
                                );

                            element.className =
                                "insight-tag";

                            element.textContent =
                                tag;

                            insightTags.appendChild(
                                element
                            );

                        }
                    );

                }


                insight.appendChild(
                    insightTitle
                );

                insight.appendChild(
                    insightTags
                );


                /* ==========================
                   READ MORE
                ========================== */

                const link =
                    document.createElement(
                        "a"
                    );

                link.className =
                    "read-more";

                link.textContent =
                    "Baca Selengkapnya →";

                link.href =
                    news.article_url;

                link.target =
                    "_blank";

                link.rel =
                    "noopener noreferrer";


                /* ==========================
                   ASSEMBLE CARD
                ========================== */

                body.appendChild(
                    meta
                );

                body.appendChild(
                    title
                );

                body.appendChild(
                    summary
                );

                body.appendChild(
                    insight
                );

                body.appendChild(
                    link
                );


                card.appendChild(
                    image
                );

                card.appendChild(
                    body
                );


                container.appendChild(
                    card
                );

            }
        );

    }

    catch (error) {

        console.error(
            "News error:",
            error
        );

        container.innerHTML = `

            <div class="loading">

                Gagal memuat berita.

                <br><br>

                Pastikan Flask dan PostgreSQL
                sedang berjalan.

            </div>

        `;

    }

}

    /* ==========================================
    LOAD AI EXECUTIVE SUMMARY
    ========================================== */

    async function loadAISummary() {

        const aiSummary =
            document.getElementById(
                "aiSummary"
            );

        if (!aiSummary) {
            return;
        }

        aiSummary.textContent =
            "Memuat analisis AI...";

        try {

            const response =
                await fetch(
                    `/api/ai-summary${sourceQuery()}`
                );

            if (!response.ok) {

                throw new Error(
                    "Gagal mengambil AI Executive Summary"
                );

            }

            const data =
                await response.json();

            if (
                data.success &&
                data.summary
            ) {

                const formattedSummary =
                data.summary
                    // Amankan karakter HTML
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")

                    // Judul ### / ##
                    .replace(
                        /^### (.+)$/gm,
                        "<h4>$1</h4>"
                    )
                    .replace(
                        /^## (.+)$/gm,
                        "<h4>$1</h4>"
                    )

                    // Bold **teks**
                    .replace(
                        /\*\*(.+?)\*\*/g,
                        "<strong>$1</strong>"
                    )

                    // Garis pemisah
                    .replace(
                        /^---$/gm,
                        "<hr>"
                    )

                    // Bullet *
                    .replace(
                        /^\* (.+)$/gm,
                        "<li>$1</li>"
                    )

                    // Bullet -
                    .replace(
                        /^- (.+)$/gm,
                        "<li>$1</li>"
                    )

                    // Baris kosong menjadi jarak
                    .replace(
                        /\n{2,}/g,
                        "<br><br>"
                    )

                    // Baris biasa
                    .replace(
                        /\n/g,
                        "<br>"
                    );

            aiSummary.innerHTML =
                formattedSummary;

            }

            else {

                aiSummary.textContent =
                    "AI Executive Summary belum tersedia.";

            }

        }

        catch (error) {

            console.error(
                "AI Summary error:",
                error
            );

            aiSummary.textContent =
                "Gagal memuat AI Executive Summary.";

        }

    }

/* ==========================================
   START DASHBOARD
========================================== */

async function loadDashboard() {

    await Promise.all([

        loadSummary(),

        loadNewsTrend(),

        loadInsights(),

        loadNews(),

        loadAISummary()

    ]);

}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        const sourceFilter =
            document.getElementById(
                "sourceFilter"
            );


        if (sourceFilter) {

            sourceFilter.addEventListener(
                "change",
                async event => {

                    currentSource =
                        event.target.value;

                    await loadDashboard();

                }
            );

        }


        loadDashboard();

    }
);