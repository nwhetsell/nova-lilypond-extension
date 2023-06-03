from lxml import etree
import re
import subprocess
from textwrap import dedent

lilypond_process = subprocess.run(["lilypond", "--loglevel=ERROR", "-"], capture_output=True, text=True, input="""
#(begin
  (for-each ly:load '("documentation-lib"
                      "lily-sort"
                      "document-functions"
                      "document-translation"
                      "document-music"
                      "document-type-predicates"
                      "document-identifiers"
                      "document-context-mods"
                      "document-backend"
                      "document-markup"
                      "document-outside-staff-priorities"
                      "document-paper-sizes"
                      "document-colors"
                      "hyphenate-internal-words"))
  (display (identifiers-doc-string))
)
""")
texinfo = lilypond_process.stdout
texinfo = re.sub(r"@lilypond\[quote,\s*verbatim\]", "@verbatim", texinfo)
texinfo = re.sub(r"@end\s+lilypond\b", "@end verbatim", texinfo)
texinfo = dedent("""\
    @macro funindex {arg}
    @end macro
    @macro q {arg}
    @end macro
    @macro qq {arg}
    @end macro
""") + texinfo

texi2any_process = subprocess.run(["/usr/local/opt/texinfo/bin/texi2any", "--xml", "-"], text=True, input=texinfo)

parser = etree.XMLParser(load_dtd=True, no_network=False)
document = etree.parse("stdin.xml", parser)

completions = document.xslt(etree.fromstring(dedent("""
    <xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:regexp="http://exslt.org/regular-expressions"
        extension-element-prefixes="regexp">
    <xsl:strip-space elements="texinfo tableitem"/>

    <!-- Default processing -->
    <xsl:template match="node()">
        <xsl:copy>
            <xsl:apply-templates select="node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="texinfo">
        <completions>
            <xsl:text>&#xA;    </xsl:text>
            <provider name="lilypond.built-in-music-functions">
                <xsl:text>&#xA;        </xsl:text>
                <syntax>lilypond</syntax>
                <xsl:text>&#xA;        </xsl:text>
                <exclude-selector>string, comment</exclude-selector>
                <xsl:text>&#xA;        </xsl:text>
                <trigger>\</trigger>
                <xsl:text>&#xA;        </xsl:text>
                <expression>(?&lt;=\\\\)[A-Za-z_-]*</expression>
                <xsl:text>&#xA;        </xsl:text>
                <set>lilypond.built-in-music-functions</set>
                <xsl:text>&#xA;    </xsl:text>
            </provider>
            <xsl:text>&#xA;</xsl:text>
            <xsl:text>&#xA;    </xsl:text>

            <set name="lilypond.built-in-music-functions" symbol="function">
                <xsl:apply-templates select="node()"/>
                <xsl:text>    </xsl:text>
            </set>
            <xsl:text>&#xA;</xsl:text>
        </completions>
    </xsl:template>

    <xsl:template match="table | tableterm | item">
        <xsl:apply-templates select="node()"/>
    </xsl:template>

    <xsl:template match="tableentry">
        <xsl:text>        </xsl:text>
        <completion>
            <xsl:attribute name="string">
                <xsl:value-of select="substring(tableterm/item/itemformat/code, 2)"/>
            </xsl:attribute>
            <xsl:if test="count(tableterm/item/itemformat/var) &gt; 0">
                <xsl:text>&#xA;            </xsl:text>
                <behavior>
                    <xsl:if test="regexp:test(string(tableitem), '\\bThis\\s+function\\s+is\\s+deprecated\\b')">
                        <xsl:attribute name="deprecated">true</xsl:attribute>
                    </xsl:if>
                    <xsl:text>&#xA;                </xsl:text>
                    <append>
                        <xsl:for-each select="tableterm/item/itemformat/var">
                            <xsl:text> </xsl:text>
                            <xsl:text>$[</xsl:text>
                            <xsl:value-of select="."/>
                            <xsl:text>]</xsl:text>
                        </xsl:for-each>
                    </append>
                    <xsl:text>&#xA;            </xsl:text>
                </behavior>
            </xsl:if>
            <xsl:if test="normalize-space(string(tableitem)) != '(undocumented; fixme)'">
                <xsl:text>&#xA;            </xsl:text>
                <description>
                    <xsl:apply-templates select="tableitem/node()"/>
                </description>
            </xsl:if>
            <xsl:text>&#xA;        </xsl:text>
        </completion>
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>

    <xsl:template match="para[position() = 1]">
        <xsl:apply-templates select="node()"/>
    </xsl:template>

    <xsl:template match="para[position() &gt; 1]">
        <xsl:text> </xsl:text>
        <xsl:apply-templates select="node()"/>
    </xsl:template>

    <xsl:template match="para/text()">
        <xsl:value-of select="regexp:replace(regexp:replace(., '\\n', 'g', ' '), ' {2,}', 'g', ' ')"/>
    </xsl:template>
    <xsl:template match="para/text()[last()]">
        <xsl:value-of select="regexp:replace(regexp:replace(regexp:replace(., '\\n', 'g', ' '), ' {2,}', 'g', ' '), '\\s+$', '', '')"/>
    </xsl:template>

    <xsl:template match="var">
        <xsl:text>⟨</xsl:text>
        <xsl:apply-templates select="node()"/>
        <xsl:text>⟩</xsl:text>
    </xsl:template>

    <xsl:template match="code | pre | samp">
        <xsl:text>`</xsl:text>
        <xsl:apply-templates select="node()"/>
        <xsl:text>`</xsl:text>
    </xsl:template>

    <xsl:template match="example">
        <xsl:text> `</xsl:text>
        <xsl:value-of select="normalize-space(string(pre))"/>
        <xsl:text>`</xsl:text>
    </xsl:template>

    <xsl:template match="filename | macro | verbatim"/>

    </xsl:stylesheet>
""")))

completions.write(
    "LilyPond.novaextension/Completions/LilyPond.xml",
    xml_declaration=True,
    encoding="UTF-8"
)
