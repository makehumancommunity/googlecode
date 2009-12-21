import sys
import os

dir_input = ""
dir_output = ""

eye_left = [12408,12409,12410,12411,12740,12741,12742,12743,12744,12745,12746,12747,12748,12749,12750,12751,12752,12753,12754,12755,12756,12757,12758,12759,12760,12761,12762,12763,12764,12765,12766,12767,12768,12769,12770,12771,12772,12773,12774,12775,12776,12777,12778,12779,12780,12781,12782,12783,12784,12785,12786,12787,12788,12789,12790,12791,12792,12793,12794,12795,12796,12797,12798,12799,12800,12801,12802,12803,12804,12805,12806,12807,12808,12809,12810,12811,12812,12813,12814,12815,12816,12817,12818,12819,12820,12821,12822,12823,12824,12825,12826,12827,12828,12829,12830,12831,12832,12833,12834,12835,12836,12837,12838,12839,12840,12841,12842,12843,12844,12845,12846,12847,12848,12849,12850,12851,12852,12853,12854,12855,12856,12857,12858,12859,12860,12861,12862,12863,12864,12865,12866,12867,12868,12869,12870,12871,12872,12873,12874,12875,12876,12877,12878,12879,12880,12881,12882,12883,12884,12885,12886,12887,12888,12889,12890,12891,12892,12893,12894,12895,12896,12897,12898,12899,12900,12901,12902,12903,12904,12905,12906,12907,12908,12909,12910,12911,12912,12913,12914,12915,12916,12917,12918,12919,12920,12921,12922,12923,12924,12925,12926,12927,12928,12929,12930,12931,12932,12933,12934,12935,12936,12937,12938,12939,12940,12941,12942,12943,12944,12945,12946,12947,12948,12949,12950,12951,12952,12953,12954,12955,12956,12957,12958,12959,12960,12961,12962,12963,12964,12965,12966,12967,12968,12969,12970,12971,12972,12973,12974,12975,12976,12977,12978,12979,12980,12981,12982,12983,12984,12985,12986,12987,12988,12989,12990,12991,12992,12993,12994,12995,12996,12997,12998,12999,13000,13001,13002,13003,13004,13005,13006,13007,13008,13009,13010,13011,13012,13013,13014,13015,13016,13017,13018,13019,13020,13021,13022,13023,13024,13025,13026,13027,13028,13029,13030,13031,13032,13033,13034,13035,13036,13037,13038,13039,13040,13041,13042,13043,13044,13045,13046,13047,13048,13049,13050,13051,13052,13053,13054,13055,13056,13057,13058,13059,13060,13061,13062,13063,13064,13065,13066,13067,13068,13069,13070,13071,13072,13073,13074,13075,13076,13077,13078,13079,13080,13081,13082,13083,13084,13085,13086,13087,13088,13089,13090,13091,13092,13093,13094,13095,13096,13097,13098,13099,13100,13101,13102,13103,13104,13105,13106,13107,13108]
eye_right = [0,1,2,3,4,5,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,6670,6683,6684,6685,6686]
mouth = [381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,568,569,570,571,572,573,574,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600,601,602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,672,673,674,675,676,677,678,679,680,681,682,683,684,685,686,687,688,689,690,691,692,693,694,695,696,697,698,699,700,701,702,703,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,722,723,724,725,726,727,728,729,730,731,732,733,734,735,736,737,738,739,740,741,742,743,744,745,746,747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,762,763,764,765,766,767,768,769,770,771,772,773,774,775,776,777,778,779,780,781,782,783,784,785,786,787,788,789,790,791,792,793,794,795,796,797,798,799,800,801,802,803,804,805,806,807,808,809,810,811,812,813,814,815,816,817,818,819,820,821,822,823,824,825,826,827,828,829,830,831,832,833,834,835,836,837,838,839,840,841,842,843,844,845,846,847,848,849,850,851,852,853,854,855,856,857,858,859,860,861,862,863,864,865,866,867,868,869,870,871,872,873,874,875,876,877,878,879,880,881,882,883,884,885,886,887,888,889,890,891,892,893,894,895,896,897,898,899,900,901,902,903,904,905,906,907,908,909,910,911,912,913,914,915,916,917,918,919,920,921,922,923,924,925,926,927,928,929,930,931,932,933,934,935,936,937,938,939,940,941,942,943,944,945,946,947,948,949,950,951,952,953,954,955,956,957,958,959,960,961,962,963,964,965,966,967,968,969,970,971,972,973,974,975,976,977,978,979,980,981,982,983,984,985,986,987,988,989,990,991,992,993,994,995,996,997,998,999,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,1012,1013,1014,1015,1016,1017,1018,1019,1020,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,1037,1038,1039,1040,1041,1042,1043,1044,1045,1046,1047,1048,1049,1050,1051,1052,1053,1054,1055,1056,1057,1058,1059,1060,1061,1062,1063,1064,1065,1066,1067,1068,1069,1070,1071,1072,1073,1074,1075,1076,1077,1078,1079,1080,1081,1082,1083,1084,1085,1086,1087,1088,1089,1090,1091,1092,1093,1094,1095,1096,1097,1098,1099,1100,1101,1102,1103,1104,1105,1106,1107,1108,1109,1110,1111,1112,1113,1114,1115,1116,1117,1118,1119,1120,1121,1122,1123,1124,1125,1126,1127,1128,1129,1130,1131,1132,1133,1134,1135,1136,1137,1138,1139,1140,1141,1142,1143,1144,1145,1146,1147,1148,1149,1150,1151,1152,1153,1154,1155,1156,1157,1158,1159,1160,1161,1162,1163,1164,1165,1166,1167,1168,1169,1170,1171,1172,1173,1174,1175,1176,1177,1178,1179,1180,1181,1182,1183,1184,1185,1186,1187,1188,1189,1190,1191,1192,1193,1194,1195,1196,1197,1198,1199,1200,1201,1202,1203,1204,1205,1206,1207,1208,1209,1210,1211,1212,1213,1214,1215,1216,1217,1218,1219,1220,1221,1222,1223,1224,1225,1226,1227,1228,1229,1230,1231,1232,1233,1234,1235,1236,1237,1238,1239,1240,1241,1242,1243,1244,1245,1246,1247,1248,1249,1250,1251,1252,1253,1254,1255,1256,1257,1258,1259,1260,1261,1262,1263,1264,1265,1266,1267,1268,1269,1270,1271,1272,1273,1274,1275,1276,1277,1278,1279,1280,1281,1282,1283,1284,1285,1286,1287,1288,1289,1290,1291,1292,1293,1294,1295,1296,1297,1298,1299,1300,1301,1302,1303,1304,1305,1306,1307,1308,1309,1310,1311,1312,1313,1314,1315,1316,1317,1318,1319,1320,1321,1322,1323,1324,1325,1326,1327,1328,1329,1330,1331,1332,1333,1334,1335,1336,1337,1338,1339,1340,1341,1342,1343,1344,1345,1346,1347,1348,1349,1350,1351,1352,1353,1354,1355,1356,1357,1358,1359,1360,1361,1362,1363,1364,1365,1366,1367,1368,1369,1370,1371,1372,1373,1374,1375,1376,1377,1378,1379,1380,1381,1382,1383,1384,1385,1386,1387,1388,1389,1390,1391,1392,1393,1394,1395,1396,1397,1398,1399,1400,1401,1402,1403,1404,1405,1406,1407,1408,1409,1410,1411,1412,1413,1414,1415,1416,1417,1418,1419,1420,1421,1422,1423,1424,1425,1426,1427,1428,1429,1430,1431,1432,1433,1434,1435,1436,1437,1438,1439,1440,1441,1442,1443,1444,1445,1446,1447,1448,1449,1450,1451,1452,1453,1454,1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465,1466,1467,1468,1469,1470,1471,1472,1473,1474,1475,1476,1477,1478,1479,1480,1481,1482,1483,1484,1485,1486,1487,1488,1489,1490,1491,1492,1493,1494,1495,1496,1497,1498,1499,1500,1501,1502,1503,1504,1505,1506,1507,1508,1509,1510,1511,1512,1513,1514,1515,1516,1517,1518,1519,1520,1521,1522,1523,1524,1525,1526,1527,1528,1529,1530,1531,1532,1533,1534,1535,1536,1537,1538,1539,1540,1541,1542,1543,1544,1545,1546,1547,1548,1549,1550,1551,1552,1553,1554,1555,1556,1557,1558,1559,1560,1561,1562,1563,1564,1565,1566,1567,1568,1569,1570,1571,1572,1573,1574,1575,1576,1577,1578,1579,1580,1581,1582,1583,1584,1585,1586,1587,1588,1589,1590,1591,1592,1593,1594,1595,1596,1597,1598,1599,1600,1601,1602,1603,1604,1605,1606,1607,1608,1609,1610,1611,1612,1613,1614,1615,1616,1617,1618,1619,1620,1621,1622,1623,1624,1625,1626,1627,1628,1629,1630,1631,1632,1633,1634,1635,1636,1637,1638,1639,1640,1641,1642,1643,1644,1645,1646,1647,1648,1649,1650,1651,1652,1653,1654,1655,1656,1657,1658,1659,1660,1661,1662,1663,1664,1665,1666,1667,1668,1669,1670,1671,1672,1673,1674,1675,1676,1677,1678,1679,1680,1681,1682,1683,1684,1685,1686,1687,1688,1689,1690,1691,1692,1693,1694,1695,1696,1697,1698,1699,1700,1701,1702,1703,1704,1705,1706,1707,1708,1709,1710,1711,1712,1713,1714,1715,1716,1717,1718,1719,1720,1721,1722,1723,1724,1725,1726,1727,1728,1729,1730,1731,1732,1733,1734,1735,1736,1737,1738,1739,1740,1741,1742,1743,1744,1745,1746,1747,1748,1749,1750,1751,1752,1753,1754,1755,1756,1757,1758,1759,1760,1761,1762,1763,1764,1765,1766,1767,1768,1769,1770,1771,1772,1773,1774,1775,1776,1777,1778,1779,1780,1781,1782,1783,1784,1785,1786,1787,1788,1789,1790,1791,1792,1793,1794,1795,1796,1797,1798,1799,1800,1801,1802,1803,1804,1805,1806,1807,1808,1809,1810,1811,1812,1813,1814,1815,1816,1817,1818,1819,1820,1821,1822,1823,1824,1825,1826,1827,1828,1829,1830,1831,1832,1833,1834,1835,1836,1837,1838,1839,1840,1841,1842,1843,1844,1845,1846,1847,1848,1849,1850,1851,1852,1853,1854,1855,1856,1857,1858,1859,1860,1861,1862,1863,1864,1865,1866,1867,1868,1869,1870,1871,1872,1873,1874,1875,1876,1877,1878,1879,1880,1881,1882,1883,1884,1885,1886,1887,1888,1889,1890,1891,1892,1893,1894,1895,1896,1897,1898,1899,1900,1901,1902,1903,1904,1905,1906,1907,1908,1909,1910,1911,1912,1913,1914,1915,1916,1917,1918,1919,1920,1921,1922,1923,1924,1925,1926,1927,1928,1929,1930,1931,1932,1933,1934,1935,1936,1937,1938,1939,1940,1941,1942,1943,1944,1945,1946,1947,1948,1949,1950,1951,1952,1953,1954,1955,1956,1957,1958,1959,1960,1961,1962,1963,1964,1965,1966,1967,1968,1969,1970,1971,1972,1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035,2036,2037,2038,2039,2040,2041,2042,2043,2044,2045,2046,2047,2048,2049,2050,2051,2052,2053,2054,2055,2056,2057,2058,2059,2060,2061,2062,2063,2064,2065,2066,2067,2068,2069,2070,2071,2072,2073,2074,2075,2076,2077,2078,2079,2080,2081,2082,2083,2084,2085,2086,2087,2088,2089,2090,2091,2092,2093,2094,2095,2096,2097,2098,2099,2100,2101,2102,2103,2104,2105,2106,2107,2108,2109,2110,2111,2112,5618,5619,5620,5621,5622,5623,5624,5625,5626,5627,5628,5629,5630,5631,5632,5633,5634,5635,5636,5637,5643,5644,5645,5646,5647,5648,5649,5650,5651,5652,5653,5654,6815,6816,6817,6818,6819,6820,6821,6822,6823,6824,6825,6826,6827,6828,6829,6830,6831,6832,6833,6834,6835,6836,6837,6838,6839,6840,6841,6842,6843,6844,6845,6846,6847,6848,6849,6850,6851,7492,7493,7494,7495,7496,7497,7498,7499,7500,7501,7502,7503,7504,7505,7506,7507,7508,7509,7510,7511,7512,7513,7514,7515,7516,7517,7518,7519,7520,7521,7522,7523,7524,7525,7526,7527,7528,7529,7530,7531,7532,7533,7534,7535,7536,7537,7538,7539,7540,7541,7542,7543,7544,7545,7546,7547,7548,7549,7550,7551,7552,7553,7554,7555,7556,7557,7558,7559,7560,7561,7562,7563,7564,7565,7566,7567,7568,7569,7570,7571,7572,7573,7574,7575,7576,7577,7578,7579,7580,7581,7582,7583,7584,7585,7586,7587,7588,7589,7590,7591,7592,7593,7594,7595,7596,7597,7598,7599,7600,7601,7602,7603,7604,7605,7606,7607,7608,7609,7610,7611,7612,7613,7614,7615,7616,7617,7618,7619,7620,7621,7622,7623,7624,7625,7626,7627,7628,7629,7630,7631,7632,7633,7634,7635,7636,7637,7638,7639,7640,7641,7642,7643,7644,7645,7646,7647,7648,7649,7650,7651,7652,7653,7654,7655,7656,7657,7658,7659,7660,7661,7662,7663,7664,7665,7666,7667,7668,7669,7670,7671,7672,7673,7674,7675,7676,7677,7678,7679,7680,7681,7682,7683,7684,7685,7686,7687,7688,7689,7690,7691,7692,7693,7694,7695,7696,7697,7698,7699,7700,7701,7702,7703,7704,7705,7706,7707,7708,7709,7710,7711,7712,7713,7714,7715,7716,7717,7718,7719,7720,7721,7722,7723,7724,7725,7726,7727,7728,7729,7730,7731,7732,7733,7734,7735,7736,7737,7738,7739,7740,7741,7742,7743,7744,7745,7746,7747,7748,7749,7750,7751,7752,7753,7754,7755,7756,7757,7758,7759,7760,7761,7762,7763,7764,7765,7766,7767,7768,7769,7770,7771,7772,7773,7774,7775,7776,7777,7778,7779,7780,7781,7782,7783,7784,7785,7786,7787,7788,7789,7790,7791,7792,7793,7794,7795,7796,7797,7798,7799,7800,7801,7802,7803,7804,7805,7806,7807,7808,7809,7810,7811,7812,7813,7814,7815,7816,7817,7818,7819,7820,7821,7822,7823,7824,7825,7826,7827,7828,7829,7830,7831,7832,7833,7834,7835,7836,7837,7838,7839,7840,7841,7842,7843,7844,7845,7846,7847,7848,7849,7850,7851,7852,7853,7854,7855,7856,7857,7858,7859,7860,7861,7862,7863,7864,7865,7866,7867,7868,7869,7870,7871,7872,7873,7874,7875,7876,7877,7878,7879,7880,7881,7882,7883,7884,7885,7886,7887,7888,7889,7890,7891,7892,7893,7894,7895,7896,7897,7898,7899,7900,7901,7902,7903,7904,7905,7906,7907,7908,7909,7910,7911,7912,7913,7914,7915,7916,7917,7918,7919,7920,7921,7922,7923,7924,7925,7926,7927,7928,7929,7930,7931,7932,7933,7934,7935,7936,7937,7938,7939,7940,7941,7942,7943,7944,7945,7946,7947,7948,7949,7950,7951,7952,7953,7954,7955,7956,7957,7958,7959,7960,7961,7962,7963,7964,7965,7966,7967,7968,7969,7970,7971,7972,7973,7974,7975,7976,7977,7978,7979,7980,7981,7982,7983,7984,7985,7986,7987,7988,7989,7990,7991,7992,7993,7994,7995,7996,7997,7998,7999,8000,8001,8002,8003,8004,8005,8006,8007,8008,8009,8010,8011,8012,8013,8014,8015,8016,8017,8018,8019,8020,8021,8022,8023,8024,8025,8026,8027,8028,8029,8030,8031,8032,8033,8034,8035,8036,8037,8038,8039,8040,8041,8042,8043,8044,8045,8046,8047,8048,8049,8050,8051,8052,8053,8054,8055,8056,8057,8058,8059,8060,8061,8062,8063,8064,8065,8066,8067,8068,8069,8070,8071,8072,8073,8074,8075,8076,8077,8078,8079,8080,8081,8082,8083,8084,8085,8086,8087,8088,8089,8090,8091,8092,8093,8094,8095,8096,8097,8098,8099,8100,8101,8102,8103,8104,8105,8106,8107,8108,8109,8110,8111,8112,8113,8114,8115,8116,8117,8118,8119,8120,8121,8122,8123,8124,8125,8126,8127,8128,8129,8130,8131,8132,8133,8134,8135,8136,8137,8138,8139,8140,8141,8142,8143,8144,8145,8146,11071,11072,11073,11074,11075,11076,11077,11078,11079,11080,11081,11082,11083,11084,11085,11086,11087,11088,11089,11090,11091,11092,11093,11094,11095,11096,11097,11098,11099,11100,11101,11102,11103,11104,11105,11106,11107,11108,11109,11110,11111,11112,11113,11114,11115,11116,11117,11118,11119,11120,11121,11122,11123,11124,11125,11126,11127,11128,11129,11130,11131,11132,11133,11134,11135,11136,11137,11138,11139,11140,11141,11142,11143,11144,11145,11146,11147,11148,11149,11150,11151,11152,11153,11154,11155,11156,11157,11158,11159,11160,11161,11162,11163,11164,11165,11166,11167,11168,11169,11170,11171,11172,11173,11174,11175,11176,11177,11178,11179,11180,11181,11182,11183,11184,11185,11186,11187,11188,11189,11190,11191,11192,11193,11194,11195,11196,11197,11198,11199,11200,11201,11202,11203,11204,11205,11206,11207,11208,11209,11210,11211,11212,11213,11214,11215,11216,11217,11218,11219,11220,11221,11222,11223,11224,11225,11226,11227,11228,11229,11230,11231,11232,11233,11234,11235,11236,11237,11238,11239,11240,11241,11242,11243,11244,11245,11246,11247,11248,11249,11250,11251,11252,11253,11254,11255,11256,11257,11258,11259,11260,11261,11262,11263,11264,11265,11266,11267,11268,11269,11270,11271,11272,11273,11274,11275,11276,11277,11278,11279,11280,11281,11282,11283,11284,11285,11286,11287,11288,11289,11290,11291,11292,11293,11294,11295,11296,11297,11298,11299,11300,11301,11302,11303,11304,11305,11306,11307,11308,11309,11310,11311,11312,11313,11314,11315,11316,11317,11318,11319,11320,11321,11322,11323,11324,11325,11326,11327,11328,11329,11330,11331,11332,11333,11334,11335,11336,11337,11338,11339,11340,11341,11342,11343,11344,11345,11346,11347,11348,11349,11350,11351,11352,11353,11354,11355,11356,11357,11358,11359,11360,11361,11362,11363,11364,11365,11366,11367,11368,11369,11370,11371,11372,11373,11374,11375,11376,11377,11378,11379,11380,11381,11382,11383,11384,11385,11386,11387,11388,11389,11390,11391,11392,11393,11394,11395,11396,11397,11398,11399,11400,11401,11402,11403,11404,11405,11406,11407,11408,11409,11410,11411,11412,11413,11414,11415,11416,11417,11418,11419,11420,11421,11422,11423,11424,11425,11426,11427,11428,11429,11430,11431,11432,11433,11434,11435,11436,11437,11438,11439,11440,11441,11442,11443,11444,11445,11446,11447,11448,11449,11450,11451,11452,11453,11454,11455,11456,11457,11458,11459,11460,11461,11462,11463,11464,11465,11466,11467,11468,11469,11470,11471,11472,11473,11474,11475,11476,11477,11478,11479,11480,11481,11482,11483,11484,11485,11486,11487,11488,11489,11490,11491,11492,11493,11494,11495,11496,11497,11498,11499,11500,11501,11502,11503,11504,11505,11506,11507,11508,11509,11510,11511,11512,11513,11514,11515,11516,11517,11518,11519,11520,11521,11522,11523,11524,11525,11526,11527,11528,11529,11530,11531,11532,11533,11534,11535,11536,11537,11538,11539,11540,11541,11542,11543,11544,11545,11546,11547,11548,11549,11550,11551,11552,11553,11554,11555,11556,11557,11558,11559,11560,11561,11562,11563,11564,11565,11566,11567,11568,11569,11570,11571,11572,11573,11574,11575,11576,11577,11578,11579,11580,11581,11582,11583,11584,11585,11586,11587,11588,11589,11590,11591,11592,11593,11594,11595,11596,11597,11598,11599,11600,11601,11602,11603,11604,11605,11606,11607,11608,11609,11610,11611,11612,11613,11614,11615,11616,11617,11618,11619,11620,11621,11622,11623,11624,11625,11626,11627,11628,11629,11630,11631,11632,11633,11634,11635,11636,11637,11638,11639,11640,11641,11642,11643,11644,11645,11646,11647,11648,11649,11650,11651,11652,11653,11654,11655,11656,11657,11658,11659,11660,11661,11662,11663,11664,11665,11666,11667,11668,11669,11670,11671,11672,11673,11674,11675,11676,11677,11678,11679,11680,11681,11682,11683,11684,11685,11686,11687,11688,11689,11690,11691,11692,11693,11694,11695,11696,11697,11698,11699,11700,11701,11702,11703,11704,11705,11706,11707,11708,11709,11710,11711,11712,11713,11714,11715,11716,11717,11718,11719,11720,11721,11722,11723,11724,11725,11726,11727,11728,11729,11730,11731,11732,11733,11734,11735,11736,11737,11738,11739,11740,11741,11742,11743,11744,11745,11746,11747,11748,11749,11750,11751,11752,11753,11754,11755,11756,11757,11758,11759,11760,11761,11762,11763,11764,11765,11766,11767,11768,11769,11770,11771,11772,11773,11774,11775,11776,11777,11778,11779,11780,11781,11782,11783,11784,11785,11786,11787,11788,11789,11790,11791,11792,11793,11794,11795,11796,11797,11798,11799,11800,11801,11802,11803,11804,11805,11806,11807,11808,11809,11810,11811,11812,11813,11814,11815,11816,11817,11818,11819,11820,11821,11822,11823,11824,11825,11826,11827,11828,11829,11830,11831,11832,11833,11834,11835,11836,11837,11838,11839,11840,11841,11842,11843,11844,11845,11846,11847,11848,11849,11850,11851,11852,11853,11854,11855,11856,11857,11858,11859,11860,11861,11862,11863,11864,11865,11866,11867,11868,11869,11870,11871,11872,11873,11874,11875,11876,11877,11878,11879,11880,11881,11882,11883,11884,11885,11886,11887,11888,11889,11890,11891,11892,11893,11894,11895,11896,11897,11898,11899,11900,11901,11902,11903,11904,11905,11906,11907,11908,11909,11910,11911,11912,11913,11914,11915,11916,11917,11918,11919,11920,11921,11922,11923,11924,11925,11926,11927,11928,11929,11930,11931,11932,11933,11934,11935,11936,11937,11938,11939,11940,11941,11942,11943,11944,11945,11946,11947,11948,11949,11950,11951,11952,11953,11954,11955,11956,11957,11958,11959,11960,11961,11962,11963,11964,11965,11966,11967,11968,11969,11970,11971,11972,11973,11974,11975,11976,11977,11978,11979,11980,11981,11982,11983,11984,11985,11986,11987,11988,11989,11990,11991,11992,11993,11994,11995,11996,11997,11998,11999,12000,12001,12002,12003,12004,12005,12006,12007,12008,12009,12010,12011,12012,12013,12014,12015,12016,12017,12018,12019,12020,12021,12022,12023,12024,12025,12026,12027,12028,12029,12030,12031,12032,12033,12034,12035,12036,12037,12038,12039,12040,12041,12042,12043,12044,12045,12046,12047,12048,12049,12050,12051,12052,12053,12054,12055,12056,12057,12058,12059,12060,12061,12062,12063,12064,12065,12066,12067,12068,12069,12070,12071,12072,12073,12074,12075,12076,12077,12078,12079,12080,12081,12082,12083,12084,12085,12086,12087,12088,12089,12090,12091,12092,12093,12094,12095,12096,12097,12098,12099,12100,12101,12102,12103,12104,12105,12106,12107,12108,12109,12110,12111,12112,12113,12114,12115,12116,12117,12118,12119,12120,12121,12122,12123,12124,12125,12126,12127,12128,12129,12130,12131,12132,12133,12134,12135,12136,12137,12138,12139,12140,12141,12142,12143,12144,12145,12146,12147,12148,12149,12150,12151,12152,12153,12154,12155,12156,12157,12158,12159,12160,12161,12162,12163,12164,12165,12166,12167,12168,12169,12170,12171,12172,12173,12174,12175,12176,12177,12178,12179,12180,12181,12182,12183,12184,12185,12186,12187,12188,12189,12190,12191,12192,12193,12194,12195,12196,12197,12198,12199,12200,12201,12202,12203,12204,12205,12206,14637]
j1  = [14031,14032,14033,14034,14035,14036] #testa
j2  = [14025,14026,14027,14028,14029,14030] #testa
j3  = [14037,14038,14039,14040,14041,14042] #collo
j4  = [14476,14477,14478,14479,14480,14481] #joint-l-finger-1-1
j5  = [14470,14471,14472,14473,14474,14475] #joint-l-finger-1-2
j6  = [14464,14465,14466,14467,14468,14469] #joint-l-finger-1-3
j7  = [14458,14459,14460,14461,14462,14463] #joint-l-finger-2-1
j8  = [14434,14435,14436,14437,14438,14439] #joint-l-finger-2-2
j9 =  [14392,14393,14394,14395,14396,14397] #joint-l-finger-2-3
j10 = [14452,14453,14454,14455,14456,14457] #joint-l-finger-3-1
j11 = [14428,14429,14430,14431,14432,14433] #joint-l-finger-3-2
j12 = [14398,14399,14400,14401,14402,14403] #joint-l-finger-3-3
j13 = [14446,14447,14448,14449,14450,14451] #joint-l-finger-4-1
j14 = [14422,14423,14424,14425,14426,14427] #joint-l-finger-4-2
j15 = [14404,14405,14406,14407,14408,14409] #joint-l-finger-4-3
j16 = [14440,14441,14442,14443,14444,14445] #joint-l-finger-5-1
j17 = [14416,14417,14418,14419,14420,14421] #joint-l-finger-5-2
j18 = [14410,14411,14412,14413,14414,14415] #joint-l-finger-5-3
j19 = [14482,14483,14484,14485,14486,14487] #joint-l-hand
j20 = [14368,14369,14370,14371,14372,14373] #joint-l-knee
j21 = [14380,14381,14382,14383,14384,14385] #joint-l-shoulder
j22 = [14302,14303,14304,14305,14306,14307] #joint-l-toe-1-1
j23 = [14296,14297,14298,14299,14300,14301] #joint-l-toe-1-2
j24 = [14320,14321,14322,14323,14324,14325] #joint-l-toe-2-1
j25 = [14314,14315,14316,14317,14318,14319] #joint-l-toe-2-2
j26 = [14308,14309,14310,14311,14312,14313] #joint-l-toe-2-3
j27 = [14332,14333,14334,14335,14336,14337] #joint-l-toe-3-1
j28 = [14284,14285,14286,14287,14288,14289] #joint-l-toe-3-2
j29 = [14326,14327,14328,14329,14330,14331] #joint-l-toe-3-3
j30 = [14344,14345,14346,14347,14348,14349] #joint-l-toe-4-1
j31 = [14278,14279,14280,14281,14282,14283] #joint-l-toe-4-2
j32 = [14338,14339,14340,14341,14342,14343] #joint-l-toe-4-3
j33 = [14356,14357,14358,14359,14360,14361] #joint-l-toe-5-1
j34 = [14272,14273,14274,14275,14276,14277] #joint-l-toe-5-2
j35 = [14350,14351,14352,14353,14354,14355] #joint-l-toe-5-3
j36 = [14362,14363,14364,14365,14366,14367] #joint-l-ankle
j37 = [14290,14291,14292,14293,14294,14295] #joint-l-clavicle
j38 = [14386,14387,14388,14389,14390,14391] #joint-l-elbow
j39 = [14374,14375,14376,14377,14378,14379] #joint-l-upper-leg
j40 = [14014,14015,14016,14017,14018,14271] #joint-pelvis
j41 = [14175,14176,14177,14178,14179,14180] #joint-r-ankle
j42 = [14247,14248,14249,14250,14251,14252] #joint-r-clavicle
j43 = [14151,14152,14153,14154,14155,14156] #joint-r-elbow
j44 = [14061,14062,14063,14064,14065,14066] #joint-r-finger-1-1
j45 = [14067,14068,14069,14070,14071,14072] #joint-r-finger-1-2
j46 = [14073,14074,14075,14076,14077,14078] #joint-r-finger-1-3
j47 = [14079,14080,14081,14082,14083,14084] #joint-r-finger-2-1
j48 = [14103,14104,14105,14106,14107,14108] #joint-r-finger-2-2
j49 = [14145,14146,14147,14148,14149,14150] #joint-r-finger-2-3
j50 = [14085,14086,14087,14088,14089,14090] #joint-r-finger-3-1
j51 = [14109,14110,14111,14112,14113,14114] #joint-r-finger-3-2
j52 = [14139,14140,14141,14142,14143,14144] #joint-r-finger-3-3
j53 = [14091,14092,14093,14094,14095,14096] #joint-r-finger-4-1
j54 = [14115,14116,14117,14118,14119,14120] #joint-r-finger-4-2
j55 = [14133,14134,14135,14136,14137,14138] #joint-r-finger-4-3
j56 = [14097,14098,14099,14100,14101,14102] #joint-r-finger-5-1
j57 = [14121,14122,14123,14124,14125,14126] #joint-r-finger-5-2
j58 = [14127,14128,14129,14130,14131,14132] #joint-r-finger-5-3
j59 = [14055,14056,14057,14058,14059,14060] #joint-r-hand
j60 = [14169,14170,14171,14172,14173,14174] #joint-r-knee
j61 = [14157,14158,14159,14160,14161,14162] #joint-r-shoulder
j62 = [14163,14164,14165,14166,14167,14168] #joint-r-upper-leg
j63 = [14049,14050,14051,14052,14053,14054] #joint-spine1
j64 = [14043,14044,14045,14046,14047,14048] #joint-spine2
j65 = [14019,14020,14021,14022,14023,14024] #joint-spine3
j66 = [14235,14236,14237,14238,14239,14240] #joint-r-toe-1-1
j67 = [14241,14242,14243,14244,14245,14246] #joint-r-toe-1-2
j68 = [14217,14218,14219,14220,14221,14222] #joint-r-toe-2-1
j69 = [14223,14224,14225,14226,14227,14228] #joint-r-toe-2-2
j70 = [14229,14230,14231,14232,14233,14234] #joint-r-toe-2-3
j71 = [14205,14206,14207,14208,14209,14210] #joint-r-toe-3-1
j72 = [14253,14254,14255,14256,14257,14258] #joint-r-toe-3-2
j73 = [14211,14212,14213,14214,14215,14216] #joint-r-toe-3-3
j74 = [14193,14194,14195,14196,14197,14198] #joint-r-toe-4-1
j75 = [14259,14260,14261,14262,14263,14264] #joint-r-toe-4-2
j76 = [14199,14200,14201,14202,14203,14204] #joint-r-toe-4-3
j77 = [14181,14182,14183,14184,14185,14186] #joint-r-toe-5-1
j78 = [14265,14266,14267,14268,14269,14270] #joint-r-toe-5-2
j79 = [14187,14188,14189,14190,14191,14192] #joint-r-toe-5-3



g_transf = [eye_left,eye_right,mouth,j1,j2,j3,j4,j5,j6,j7,j8,j9,j10,j11,j12,j13,j14,j15,j16,j17,j18,j19,j20,j21,j22,j23,j24,j25,j26,j27,j28,j29,j30,j31,j32,j33,j34,j35,j36,j37,j38,j39,j40,j41,j42,j43,j44,j45,j46,j47,j48,j49,j50,j51,j52,j53,j54,j55,j56,j57,j58,j59,j60,j61,j62,j63,j64,j65,j66,j67,j68,j69,j70,j71,j72,j73,j74,j75,j76,j77,j78,j79]


originalVerts = [] #Original base mesh coords

target = [] #struttura del target
indexT = [] #lista indici del target

class vert:
    co = []
    index = 0
    
    def __init__(self, co, index):
        self.co = co
        self.index = index
        
 
def createTarget(file):
    #apro il file target
    try:
        fileDescriptor = open(dir_input+file, "r")
    except:
        print "Errore apertura file %s",(file)
        return  None    
    
    linesTarget = fileDescriptor.readlines()
    
    #preparo struttura target
    for l in linesTarget:
        words = l.split(" ")
        index = int(words[0])
        target.append(vert([float(words[1]), float(words[2]), float(words[3])], index))
        indexT.append(index)
    fileDescriptor.close()
    
           
def calcVerts():
    #apro il file conf  
    try:
        confDescriptor = open("conf.txt", "r")
    except:
        print "Errore apertura file %s",("conf.txt")
        return  None        
    
    linesConf   = confDescriptor.readlines()
        
    #per ogni v in conf
    for l in linesConf:
        words = l.split(" ")
        index = int(words[0]) #index del vertice nel conf
        neighbor = int(words[1]) #index del vertice vicino nel conf
        distx = float(words[2]) #distanza su x
        disty = float(words[3]) #distanza su y
        distz = float(words[4]) #distanza su z
        #trovo il vicino nella struttura del target
        try:
            offset = indexT.index(neighbor)
            #prendo x y z e aggiungo spostamento
            x =  (originalVerts[neighbor][0] - originalVerts[index][0]) + target[offset].co[0] + distx
            y =  (originalVerts[neighbor][1] - originalVerts[index][1]) + target[offset].co[1] + disty
            z =  (originalVerts[neighbor][2] - originalVerts[index][2]) + target[offset].co[2] + distz
            
            #trovo vertice in struttura e cambio le coordinate
            offsetV = indexT.index(index)
            target[offsetV].co[0] = x
            target[offsetV].co[1] = y
            target[offsetV].co[2] = z
        except:
            print "errore"
            

def eyes():
    #prendo ingombro e baricentro
    for g in g_transf:
        try:
            offset = indexT.index(g[0])
            maxx = target[offset].co[0]
            minx = target[offset].co[0]
            maxy = target[offset].co[1]
            miny = target[offset].co[1]
            maxz = target[offset].co[2]
            minz = target[offset].co[2]
            maxxc = target[offset].co[0] + originalVerts[g[0]][0]
            minxc = target[offset].co[0] + originalVerts[g[0]][0]
            maxyc = target[offset].co[1] + originalVerts[g[0]][1]
            minyc = target[offset].co[1] + originalVerts[g[0]][1]
            maxzc = target[offset].co[2] + originalVerts[g[0]][2]
            minzc = target[offset].co[2] + originalVerts[g[0]][2]
            maxxt = originalVerts[g[0]][0]
            minxt = originalVerts[g[0]][0]
            maxyt = originalVerts[g[0]][1]
            minyt = originalVerts[g[0]][1]
            maxzt = originalVerts[g[0]][2]
            minzt = originalVerts[g[0]][2]
        except:
            pass
        for v in g:
            try:
                offset = indexT.index(v)
                x = target[offset].co[0] + originalVerts[v][0]
                y = target[offset].co[0] + originalVerts[v][0]
                z = target[offset].co[0] + originalVerts[v][0]
                xt = originalVerts[v][0]
                yt = originalVerts[v][0]
                zt = originalVerts[v][0]
                if target[offset].co[0] > maxx:
                    maxx = target[offset].co[0]
                if target[offset].co[0] < minx:
                    minx = target[offset].co[0]
                if target[offset].co[1] > maxy:
                    maxy = target[offset].co[1]
                if target[offset].co[1] < miny:
                    miny = target[offset].co[1]
                if target[offset].co[2] > maxz:
                    maxz = target[offset].co[2]
                if target[offset].co[2] < minz:
                    minz = target[offset].co[2]
                if x > maxxc:
                    maxxc = x
                if x < minxc:
                    minxc = x
                if y > maxyc:
                    maxyc = y
                if y < minyc:
                    minyc = y
                if z > maxzc:
                    maxzc = z
                if z < minzc:
                    minzc = z
                if xt > maxxt:
                    maxxt = xt
                if xt < minxt:
                    minxt = xt
                if yt > maxyt:
                    maxyt = yt
                if yt < minyt:
                    minyt = yt
                if zt > maxzt:
                    maxzt = zt
                if zt < minzt:
                    minzt = zt
            except:
                pass
                 
        #ripristino la forma
        for v in g:
            try:
                offset = indexT.index(v)
                target[offset].co[0] = originalVerts[v][0]
                target[offset].co[1] = originalVerts[v][1]
                target[offset].co[2] = originalVerts[v][2]
            except:
                pass
                
        #scalo
        distx = maxxc - minxc
        disty = maxyc - minyc
        distz = maxzc - minzc
        distxt = maxxt - minxt
        distyt = maxyt - minyt
        distzt = maxzt - minzt
        fact = ((distx/distxt)+(disty/distyt)+(distz/distzt))/3
        #print (distx/distxt), (disty/distyt), (distz/distzt)
       # print fact
        fact = min((distx/distxt),(disty/distyt)+(distz/distzt))
        for v in g:
            try:
                offset = indexT.index(v)
                target[offset].co[0] = target[offset].co[0] * fact
                target[offset].co[1] = target[offset].co[1] * fact
                target[offset].co[2] = target[offset].co[2] * fact
            except:
                pass

        
        
        #sposto le coordinate           
        for v in g:
            try:
                offset = indexT.index(v)
                target[offset].co[0] = target[offset].co[0] - originalVerts[v][0]
                target[offset].co[1] = target[offset].co[1] - originalVerts[v][1]
                target[offset].co[2] = target[offset].co[2] - originalVerts[v][2]
            except:
                pass
                
        #verificare lo spostamento con il target attuale e quello salvato
        try:
            offset = indexT.index(g[0])
            maxxn = target[offset].co[0]
            minxn = target[offset].co[0]
            maxyn = target[offset].co[1]
            minyn = target[offset].co[1]
            maxzn = target[offset].co[2]
            minzn = target[offset].co[2]
        except:
            pass
        for v in g:
            try:
                offset = indexT.index(v)
                if target[offset].co[0] > maxxn:
                    maxxn = target[offset].co[0]
                if target[offset].co[0] < minxn:
                    minxn = target[offset].co[0]
                if target[offset].co[1] > maxyn:
                    maxyn = target[offset].co[1]
                if target[offset].co[1] < minyn:
                    minyn = target[offset].co[1]
                if target[offset].co[2] > maxzn:
                    maxzn = target[offset].co[2]
                if target[offset].co[2] < minzn:
                    minzn = target[offset].co[2]
            except:
                pass
        
        center  = [(minx + (maxx - minx)/2), (miny + (maxy - miny)/2), (minz + (maxz - minz)/2)] 
        centern = [(minxn + (maxxn - minxn)/2), (minyn + (maxyn - minyn)/2), (minzn + (maxzn - minzn)/2)] 
        for v in g:
            try:
                offset = indexT.index(v)
                target[offset].co[0] = target[offset].co[0] + (center[0] - centern[0])
                target[offset].co[1] = target[offset].co[1] + (center[1] - centern[1])
                target[offset].co[2] = target[offset].co[2] + (center[2] - centern[2])
            except:
                pass
           
   
def saveTarget(file):
    #apro target in scrittura   
    try:
        fileDescriptor = open(dir_output+file, "w")
    except:
        print "Errore apertura file %s",(file)
        return  None    
    #riscrivo target secondo struttura
    for i in target:
        fileDescriptor.write("%d %f %f %f\n" % (i.index, i.co[0], i.co[1], i.co[2]))
    fileDescriptor.close()         
                

    

def loadInitialBaseCoords(path):
    """
    This function is a little utility function to load only the vertex data 
    from a wavefront obj file.

    Parameters
    ----------

    path:
        *string*. A string containing the operating system path to the 
        file that contains the wavefront obj.

    """
    try:
        fileDescriptor = open(path)
    except:
        print "Error opening %s file"%(path)
        return
    data = fileDescriptor.readline()
    vertsCoo = []
    while data:
        dataList = data.split()
        if dataList[0] == "v":
            co = (float(dataList[1]),\
                    float(dataList[2]),\
                    float(dataList[3]))
            vertsCoo.append(co)
        data = fileDescriptor.readline()
    fileDescriptor.close()
    return vertsCoo
        
#controllo errori argomenti
if __name__ == '__main__' :
    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " input_dir output_dir"
        sys.exit()
        
    dir_input = sys.argv[1]
    dir_output = sys.argv[2]

    originalVerts = loadInitialBaseCoords("base.obj")
    #apertura directory
    file_list = os.listdir(dir_input)
    #modifica i vertici e salva i file nella nuova directory
    for f in file_list:
        target = []
        indexT = []
        createTarget(f)
        calcVerts()
        #print "*********", f , "*************"
        eyes()     
        saveTarget(f)

