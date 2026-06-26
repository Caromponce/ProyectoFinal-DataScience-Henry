import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>

        :root{
            --henry-yellow:#F2E40C;
            --henry-purple:#7C3AED;
            --henry-red:#E8472B;
            --henry-green:#1F7A44;
            --henry-text:#1A1A1A;
            --henry-gray:#555555;
            --henry-border:#E4E4E0;
            --henry-card:#F6F6F4;
        }

        html, body, [class*="css"]{
            font-family: "Inter","Poppins",sans-serif;
            font-size:17px;
            color:var(--henry-text);
        }

        .block-container{
            max-width:1200px;
            padding-top:3rem;
            padding-bottom:3rem;
        }

        h1{
            font-size:48px !important;
            line-height:1.1 !important;
            margin-bottom:18px !important;
        }

        h2{
            font-size:32px !important;
        }

        h3{
            font-size:26px !important;
        }

        p, li{
            font-size:17px !important;
            line-height:1.65 !important;
        }

        .henry-highlight{
            display:inline;
            background:linear-gradient(
                transparent 58%,
                var(--henry-yellow) 58%
            );
            font-weight:800;
            padding:0 6px;
        }

        .henry-tag{
            display:inline-block;
            background:var(--henry-purple);
            color:white;
            padding:6px 14px;
            border-radius:999px;
            font-size:14px;
            font-weight:700;
            margin-bottom:16px;
        }

        .henry-card{
            background:var(--henry-card);
            padding:22px;
            border-radius:16px;
            border:1px solid var(--henry-border);
            box-shadow:0 6px 18px rgba(0,0,0,.05);
            margin-bottom:18px;
        }

        .henry-bullet{
            color:var(--henry-red);
            font-weight:900;
            margin-right:8px;
        }

        .status-card{
            background:white;
            border:1px solid var(--henry-border);
            border-radius:16px;
            padding:18px;
            box-shadow:0 6px 18px rgba(0,0,0,.05);
            min-height:120px;
        }

        .status-title{
            font-size:14px;
            color:var(--henry-gray);
            font-weight:700;
        }

        .status-value{
            font-size:28px;
            font-weight:900;
        }

        .status-ok{
            color:var(--henry-green);
        }

        .status-progress{
            color:#C47A00;
        }

        .status-pending{
            color:#7A6E8C;
        }

        div.stButton > button{
            background:var(--henry-yellow);
            color:black;
            border:none;
            border-radius:999px;
            font-weight:800;
            padding:.7rem 1.2rem;
        }

        div.stButton > button:hover{
            background:#dfd200;
            color:black;
        }

        /* ---------- SIDEBAR ---------- */

        section[data-testid="stSidebar"]{
            background:#F6F6F4;
            border-right:1px solid #E4E4E0;
        }

        section[data-testid="stSidebar"] img{
            display:block;
            margin:auto;
            margin-top:10px;
            margin-bottom:10px;
        }

        section[data-testid="stSidebar"] h2{
            text-align:center;
            margin-bottom:4px;
            font-size:22px !important;
        }

        section[data-testid="stSidebar"] p{
            text-align:center;
            color:#666;
            font-size:13px !important;
            line-height:1.4;
        }

        section[data-testid="stSidebar"] hr{
            margin-top:18px;
            margin-bottom:18px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )