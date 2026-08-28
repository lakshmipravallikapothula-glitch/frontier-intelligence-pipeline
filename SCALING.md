\# Scalability Architecture



\## Overview



The current project is a Python prototype designed to demonstrate an AI data-ingestion pipeline.



The prototype uses:



\- Python

\- HTTPX

\- BeautifulSoup

\- OpenAI structured extraction

\- Pydantic

\- SQLite

\- GitHub API

\- Automated testing



SQLite is sufficient for the assessment prototype. For production workloads containing 100,000+ records, the architecture can be extended using a message queue, multiple workers, PostgreSQL, caching, and observability.



\---



\## Current Prototype Architecture



```text

&#x20;                   Input URL

&#x20;                      |

&#x20;                      v

&#x20;               +--------------+

&#x20;               |    Crawler   |

&#x20;               +--------------+

&#x20;                      |

&#x20;                      v

&#x20;            HTTP 429 Retry Logic

&#x20;                      |

&#x20;                      v

&#x20;             HTML / Raw Content

&#x20;                      |

&#x20;                      v

&#x20;               +--------------+

&#x20;               | BeautifulSoup|

&#x20;               +--------------+

&#x20;                      |

&#x20;                      v

&#x20;               Readable Text

&#x20;                      |

&#x20;                      v

&#x20;            +------------------+

&#x20;            | LLM Extraction   |

&#x20;            | Pydantic Schema  |

&#x20;            +------------------+

&#x20;                      |

&#x20;                413 Too Large?

&#x20;                   /       \\

&#x20;                 No         Yes

&#x20;                 |           |

&#x20;                 |      +---------+

&#x20;                 |      | Chunking|

&#x20;                 |      +---------+

&#x20;                 |           |

&#x20;                 |      LLM per chunk

&#x20;                 |           |

&#x20;                 |      Merge results

&#x20;                 |           |

&#x20;                 +-----+-----+

&#x20;                       |

&#x20;                       v

&#x20;              Entity Resolution

&#x20;                       |

&#x20;                       v

&#x20;                    SQLite

&#x20;                       |

&#x20;             +---------+---------+

&#x20;             |                   |

&#x20;             v                   v

&#x20;       Organizations       Documents

&#x20;                                 |

&#x20;                                 v

&#x20;                        GitHub Metrics

