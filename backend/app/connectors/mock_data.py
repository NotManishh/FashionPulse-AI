from datetime import datetime, timezone, timedelta
from typing import List
from app.connectors.base import NormalizedContentItem


def get_demo_fashion_content() -> List[NormalizedContentItem]:
    """
    Returns realistic demonstration content across Reddit, Instagram, and YouTube
    explicitly labeled with is_demo=True.
    Used for local testing and initial evaluation prior to live API credentials.
    """
    now = datetime.now(timezone.utc)
    
    items = [
        # Reddit Posts
        NormalizedContentItem(
            platform="reddit",
            external_id="reddit_post_001",
            title="Why oversized hoodies and baggy wide-leg jeans are dominating street style this season",
            content_text="Ever since the shift away from skinny fits, oversized hoodies paired with baggy wide-leg denim have become the universal uniform. Silhouette drape and heavy fleece fabrics are everything right now.",
            author_id="user_reddit_style42",
            permalink="https://reddit.com/r/streetwear/comments/demo001",
            published_at=now - timedelta(hours=3),
            raw_metrics={"score": 842, "num_comments": 142},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="reddit",
            external_id="reddit_post_002",
            title="The shift from loud logos to Quiet Luxury: Loro Piana, Brunello Cucinelli aesthetics",
            content_text="Discussing the quiet luxury trend: structured cashmere knitwear, relaxed linen trousers, and subtle minimalist sneakers. People want quality materials without giant logos.",
            author_id="user_reddit_tailored",
            permalink="https://reddit.com/r/malefashionadvice/comments/demo002",
            published_at=now - timedelta(hours=7),
            raw_metrics={"score": 1250, "num_comments": 230},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="reddit",
            external_id="reddit_post_003",
            title="Utility wear: Are cargo pants and techwear nylon jackets here to stay?",
            content_text="I've been wearing cargo pants with functional pockets and water-repellent techwear shell jackets all autumn. Pair them with chunky lug-sole loafers or hiking boots.",
            author_id="user_reddit_gorp",
            permalink="https://reddit.com/r/fashion/comments/demo003",
            published_at=now - timedelta(hours=14),
            raw_metrics={"score": 620, "num_comments": 89},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="reddit",
            external_id="reddit_post_004",
            title="Coquette balletcore bows and lace tops trend analysis",
            content_text="The coquette aesthetic with ribbon hair bows, lace trim cardigans, and delicate ballet flats has officially crossed from TikTok into mainstream retail.",
            author_id="user_reddit_coquette",
            permalink="https://reddit.com/r/femalefashionadvice/comments/demo004",
            published_at=now - timedelta(hours=20),
            raw_metrics={"score": 930, "num_comments": 178},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="reddit",
            external_id="reddit_post_005",
            title="Vintage streetwear vs Y2K revival - thrifting oversized bomber jackets",
            content_text="Thrifting vintage leather bomber jackets and 90s graphic tees. Paired with loose-fit denim and low profile minimalist sneakers.",
            author_id="user_reddit_thrift",
            permalink="https://reddit.com/r/streetwear/comments/demo005",
            published_at=now - timedelta(hours=28),
            raw_metrics={"score": 510, "num_comments": 64},
            is_demo=True
        ),

        # Instagram Posts
        NormalizedContentItem(
            platform="instagram",
            external_id="insta_media_101",
            title=None,
            content_text="Weekend styling: heavyweight oversized hoodie layered under a cropped tailored blazer. Keeping the silhouette relaxed with wide-leg denim. #fashiontrends #ootd #streetwearfashion #widelegjeans",
            author_id="insta_creator_milan",
            permalink="https://instagram.com/p/demo101",
            published_at=now - timedelta(hours=4),
            raw_metrics={"like_count": 4820, "comments_count": 134},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="instagram",
            external_id="insta_media_102",
            title=None,
            content_text="Effortless elegance. Clean monochrome palette with relaxed linen trousers and minimalist sneakers. True quiet luxury aesthetic. #quietluxury #oldmoney #minimalstyle #neutralpalette",
            author_id="insta_creator_paris",
            permalink="https://instagram.com/p/demo102",
            published_at=now - timedelta(hours=9),
            raw_metrics={"like_count": 12400, "comments_count": 310},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="instagram",
            external_id="insta_media_103",
            title=None,
            content_text="Balletcore moodboard 🎀 Pastel cardigan, pleated skirt, ribbon details. Love the playful coquette energy! #coquetteaesthetic #balletcore #softglam #girlhood",
            author_id="insta_creator_tokyo",
            permalink="https://instagram.com/p/demo103",
            published_at=now - timedelta(hours=18),
            raw_metrics={"like_count": 8900, "comments_count": 245},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="instagram",
            external_id="insta_media_104",
            title=None,
            content_text="Cargo pants styled 3 different ways: Street, Casual, and Night out. Chunky lug-sole loafers elevate any baggy cargo fit. #cargopants #streetwear #outfitinspo",
            author_id="insta_creator_london",
            permalink="https://instagram.com/p/demo104",
            published_at=now - timedelta(hours=25),
            raw_metrics={"like_count": 6700, "comments_count": 182},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="instagram",
            external_id="insta_media_105",
            title=None,
            content_text="Cyberpunk meets Tokyo transit. All-black techwear jacket with weatherproof straps and modular bag accessories. #techwear #gorpcore #futuristicfashion",
            author_id="insta_creator_berlin",
            permalink="https://instagram.com/p/demo105",
            published_at=now - timedelta(hours=36),
            raw_metrics={"like_count": 5200, "comments_count": 94},
            is_demo=True
        ),

        # YouTube Videos
        NormalizedContentItem(
            platform="youtube",
            external_id="yt_vid_201",
            title="Top 10 Fashion Trends You Need to Know (Streetwear & Runway Breakdown)",
            content_text="Full breakdown of the massive resurgence in wide-leg jeans, boxy oversized hoodies, and why minimalist sneakers are replacing loud hype shoes. Complete styling guide.",
            author_id="UC_fashionpulse_yt1",
            permalink="https://youtube.com/watch?v=demo201",
            published_at=now - timedelta(hours=5),
            raw_metrics={"views": 84500, "likes": 5600, "comments": 420},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="youtube",
            external_id="yt_vid_202",
            title="How to Dress 'Quiet Luxury' Without Spending Millions | Capsule Wardrobe",
            content_text="The quiet luxury aesthetic broken down into practical pieces: linen trousers, merino wool knits, classic trench coats, and clean understated footwear.",
            author_id="UC_fashionpulse_yt2",
            permalink="https://youtube.com/watch?v=demo202",
            published_at=now - timedelta(hours=12),
            raw_metrics={"views": 142000, "likes": 9800, "comments": 680},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="youtube",
            external_id="yt_vid_203",
            title="HUGE Vintage Streetwear & Thrift Haul | 90s Leather & Cargo Pants",
            content_text="I went thrifting in Tokyo and found incredible vintage streetwear pieces: oversized bomber jackets, distressed denim, and multi-pocket cargo pants.",
            author_id="UC_fashionpulse_yt3",
            permalink="https://youtube.com/watch?v=demo203",
            published_at=now - timedelta(hours=22),
            raw_metrics={"views": 53000, "likes": 3900, "comments": 290},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="youtube",
            external_id="yt_vid_204",
            title="Why Everyone Is Obsessed With Coquette Aesthetic & Balletcore",
            content_text="Explaining the cultural phenomenon of coquette fashion, feminine lace details, ribbons, and how brands are adapting balletcore into ready-to-wear.",
            author_id="UC_fashionpulse_yt4",
            permalink="https://youtube.com/watch?v=demo204",
            published_at=now - timedelta(hours=30),
            raw_metrics={"views": 67000, "likes": 4700, "comments": 350},
            is_demo=True
        ),
        NormalizedContentItem(
            platform="youtube",
            external_id="yt_vid_205",
            title="Techwear in 2026: Functional Gorpcore Aesthetics Tested in Rainy City",
            content_text="Testing technical fabrics, water-resistant shells, modular pockets, and ergonomic tailoring. Gorpcore outdoor style meets futuristic urban aesthetics.",
            author_id="UC_fashionpulse_yt5",
            permalink="https://youtube.com/watch?v=demo205",
            published_at=now - timedelta(hours=40),
            raw_metrics={"views": 41000, "likes": 2800, "comments": 210},
            is_demo=True
        )
    ]
    return items
