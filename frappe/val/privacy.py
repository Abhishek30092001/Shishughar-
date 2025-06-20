import frappe
from werkzeug.wrappers import Response

@frappe.whitelist(allow_guest=True)
def privacy():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PRIVACY NOTICE – Shishughar</title>
        <style>
            /* General Styles */
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                font-family: 'Cambria', serif;
                background-color: #f4f6f9;
                color: #333;
                line-height: 1.6;
                padding-top: 60px;
            }
            .container {
                width: 100%;
                max-width: 1300px;
                margin: 20px auto;
                padding: 25px;
                background: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }
            h1, h2, h3 {
                color: #5979aa;
            }
            h1 {
                font-size: 28px;
                text-align: center;
                border-bottom: 3px solid #5979aa;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }
            h2 {
                font-size: 22px;
                margin-top: 30px;
                color: #5979aa;
                border-left: 5px solid #5979aa;
                padding-left: 10px;
            }
            h3 {
                font-size: 18px;
                margin-top: 20px;
                color: #1d6bb5;
            }
            p, ul {
                font-size: 16px;
                line-height: 1.6;
            }
            ul {
                padding-left: 20px;
            }
            ul li {
                margin-bottom: 10px;
            }
            a {
                color: #5979aa;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                color: #1d6bb5;
                text-decoration: underline;
            }

            /* Navigation Bar */
            .navbar {
                position: fixed;
                top: 0;
                width: 100%;
                background: #5979aa;
                padding: 15px 0;
                text-align: center;
                color: #fff;
                font-size: 18px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                z-index: 1000;
            }

            /* Footer */
            .footer {
                text-align: center;
                padding: 15px;
                background: #5979aa;
                color: #fff;
                font-size: 14px;
                position: relative;
                width: 100%;
                bottom: 0;
            }
            .footer a {
                color: #f1c40f;
            }
            .footer a:hover {
                color: #d4ac0d;
                text-decoration: underline;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .container {
                    width: 90%;
                    padding: 15px;
                }
                h1 {
                    font-size: 24px;
                }
                h2 {
                    font-size: 20px;
                }
                .navbar {
                    font-size: 16px;
                    padding: 10px 0;
                }
                .footer {
                    font-size: 12px;
                    padding: 10px;
                }
            }

            @media (max-width: 480px) {
                body {
                    padding-top: 50px;
                }
                .container {
                    width: 95%;
                    padding: 10px;
                }
                h1 {
                    font-size: 22px;
                }
                h2 {
                    font-size: 18px;
                }
                p, ul {
                    font-size: 14px;
                }
            }
        </style>
    </head>
    <body>
        <div class="navbar">
            PRIVACY NOTICE
        </div>

        <div class="container">
            <h1>Terms of Use & Privacy Policy</h1>
    
            <h2>1. Introduction</h2>
            <p>Azim Premji Philanthropic Initiatives Private Limited (“Licensor”/ “We”/ “Us”) is implementing a programme (“Programme”) for supporting decentralized community-based day care centres/creches (“Shishughar”) where caregivers may leave their children. The Licensor has partnered with certain non-government organizations (“Partner NGOs”/ “Licensees”) to implement the Programme. To support the Partner NGOs/Licensees to implement the Programme, the Licensor has developed a mobile application (“Shishughar App”) and a website (“Shishughar Website”) (collectively referred to as “Services”). Partner NGOs/Licensees may use and access the Services by creating an account on the said website/application. Any person who creates an account, accesses and uses the Services on behalf of the Partner NGOs shall be construed as “User/s” of the Services. 
            The Licensor, Licensee and User may hereinafter be individually referred to as “Party” and jointly as “Parties”.
            The Licensor has sufficient rights in the Services and has agreed to provide the Licensee and Users access to the Services, subject to these Terms of Use (“Terms”).
            </p>

            <h2>2.Creation of a User Account on the Shishughar Website</h2>
            <p1><strong style="color: black; font-weight: bold;">2.1.</strong> In order to use the Services, an account (“Account”) must be created on the Shishughar Website by providing details such as name, email address, contact number of the User (collectively, “User’s Information”). The User shall ensure that the User’s Information provided is accurate and up to date at all times. 
            </p1> <br>
            <p2><strong style="color: black; font-weight: bold;">2.2.</strong> Upon successful creation of the Account, the User shall have a username and password through which the User may access and use the Services on behalf of the Licensee. The User’s Account shall be personal, confidential and non-transferable to any third party.
            </p2>
            <br>
            <p3><strong style="color: black; font-weight: bold;">2.3.</strong> Each person shall only create one Account and will not create successive Accounts unless the previous Accounts are duly deleted. Each Account shall correlate to 01 (one) User at a time. 
            </p3> <br>
            <p4><strong style="color: black; font-weight: bold;">2.4.</strong> By providing the User Information, the User agrees that the contact number furnished for Account creation is not part of any “do not call” registry or its equivalent, anywhere in the world and that the Licensor may contact the User to send notices, or alerts from time to time.
            </p4> 
            <br>
            <p5><strong style="color: black; font-weight: bold;">2.5.</strong> Licensor reserves the right to amend, modify, restrict, suspend or discontinue the User’s access to any or all parts of the Services without prior notice. If User’s Account has been disabled, suspended or discontinued by Licensor, User will not create a new Account, whether with their information, or otherwise. 
            </p5>
            <br>
            <p6><strong style="color: black; font-weight: bold;">2.6.</strong> The Licensor shall not retain User’s or information of beneficiaries of the Programme (“Beneficiary Information”) uploaded on the Shishughar App or Shishughar Website by the User on behalf of the Licensee for a period more than necessary to fulfil the purposes outlined in the Privacy Policy annexed to these Terms, unless a longer retention period is required by law or for directly related legitimate business purposes. Please refer to the Privacy Policy annexed hereto to know more about the rights available to the Users or beneficiaries of the Programme (“Beneficiaries”) with respect to the User’s Information or Beneficiary Information uploaded on the Shishughar App or Shishughar Website.
            </p6>
            <br>
            <p7><strong style="color: black; font-weight: bold;">2.7.</strong> In the event that a User is no longer associated with or represents the Licensee, the Licensee shall solely be responsible for all actions pertaining to such User’s Account such as but not limited to updating/deletion of User Information for the purpose of transfer of the Account to another User or deletion of such User Account. During the process of transfer or deletion of the User Account, as the case may be, the Licensee shall also be responsible for all actions pertaining to the Beneficiary Information uploaded on the said User Account.
            <p7>
            <br>
            <p8><strong style="color: black; font-weight: bold;">2.8.</strong> By accessing or using the Services, the Licensees and its Users agree to be bound by these Terms and the Licensor’s other policies (if any) made available on the Shishughar App or Shishughar Website and also acknowledges that it creates a binding contract between the Licensor and the User as well as the Licensor and Licensee.  
            <p8>
            <h3><strong style="color: black; font-weight: bold;">3.Representations and Warranties:</strong></h3>
            <p><strong style="color: black; font-weight: bold;">3.1.</strong> Mutual Warranties:
            Each Party represents, warrants and covenants that: (i) it has the full right, power, and authority to adhere to these Terms and to discharge its respective obligations hereunder; and (ii) it shall comply with all applicable laws in the conduct of its business and in the performance of its obligations under these Terms. 
            </p>
            <br>
            <p><strong style="color: black; font-weight: bold;">3.2.Licensee’s/User’s Warranties:</strong> 
            The Licensee/User (as the case may be) represents, warrants and covenants that-
            </p>
            <p1>
            <strong style="color: black; font-weight: bold;">3.2.1.</strong>The Licensee and its Users shall jointly be responsible for all activities that occur while using the Account on the Shishughar App or Shishughar Website. 
            </p1>
            <br>
            <p2>
            <strong style="color: black; font-weight: bold;">3.2.2.</strong> The Licensor and its Users shall jointly be responsible for the accuracy, quality, integrity, legality, reliability, and appropriateness of all information uploaded on the Shishughar App or Shishughar Website including but not limited to the User’s Information and Beneficiary Information. 
            </p2>
            <br>
            <p3>
            <strong style="color: black; font-weight: bold;">3.2.3.</strong> The Licensee and its Users shall use reasonable efforts to prevent unauthorized access to, or use of the Services and – <br>
            i.In case of Licensees - notify the Licensor promptly of any such unauthorized use or breach of security. <br>
            ii.In case of Users – either promptly notify the Licensee, who shall in turn notify the Licensor OR directly notify the Licensor, of any such unauthorized use or breach of security. 
            </p3><br>
            <p4>
            <strong style="color: black; font-weight: bold;">3.2.4.</strong>Licensee and its Users shall comply with applicable laws.<br>
            <strong style="color: black; font-weight: bold;">3.2.5.</strong>The Services shall not be misused in any manner for any purpose, which may be deemed as objectionable by the Licensor.<br>
            <strong style="color: black; font-weight: bold;">3.2.6.</strong> The Licensee or any of its Users shall not:<br>
            i.	reverse engineer, decompile, disassemble, or otherwise attempt to discern the source code, object code, underlying structures, algorithms, ideas, know-how or any other information of or related to the Services;<br>
            ii.	alter, adapt, dilute, modify, translate, or create derivatives based on the Services; 
            iii.	make any copies of the Services;<br>
            iv.	send spam or otherwise duplicative or unsolicited messages in violation of applicable laws;
            v.	resell, distribute, or sublicense the Services;<br> 
            vi.	make the Services available to or otherwise allow any third party other than the Licensees from the respective Partner NGOs to use or access the Services ; <br>
            vii.	remove or modify any proprietary marking or restrictive legends placed on the Services; <br>
            viii.	introduce into the Services any software, virus, worm, “back door”, Trojan Horse, or similar harmful code;<br> 
            ix.	attempt in any way to alter, modify, eliminate, conceal, or otherwise render inoperable or ineffective the website tags, source codes, links, pixels, modules or other data provided by or obtained from the Licensor that allows the Licensor to measure the performance and provide the Services; <br>
            x.	use the Services in order to (A) build a competitive product or service, (B) build a product or service using similar ideas, features, functions or graphics of the Services, or (C) copy any ideas, features, functions or graphics of the Services ;
            xi.	extract data from the Services ;<br>
            xii.	facilitate or encourage any violation of this Agreement or Licensor’s other Policies (if any);<br>
            xiii.	make any statement(s) or comment(s) on the Services which is inaccurate, false, unfair or defamatory to the Licensor or other Licensees or which violates the legal right of others;<br>
            xiv.	directly or indirectly solicit the Account Information of other Licensees or access or try to access any Account which does not belong to such Licensee;<br>
            xv.	attempt to or gain unauthorized access to any portion or feature of the Services including other Licensee’s Accounts, or any other systems or networks connected to the Services or to any server, computer, network, or to any portion of the Services by hacking, password “mining” or any other illegitimate means; <br>
            xvi.probe, scan or test the vulnerability of the Services or any network connected to the Services or breach the security or authentication measures on the Services or any network connected to the Services ; or<>br>
            xvii.	upload, host, display, publish, share or otherwise make available on the Shishughar App or Shishughar Website any content or information that belongs to anyone else without their consent as per applicable laws including but not limited to data protection laws.<br>
            <strong style="color: black; font-weight: bold;">3.2.7.</strong>If the Licensee or any of its Users violate any condition in Clauses 3.2.6 (i) to 3.2.6(xvii) above, the Licensor shall have the right, in its sole discretion, to deny the Licensee and User access to the Services , or any portion thereof, without any notice. Further, the Licensor reserves the right to restrict access to the Services , if the Licensee/User has been or Licensor has reasonable grounds to believe that the Licensee/User has been convicted of an offence under applicable laws.<br>
            <strong style="color: black; font-weight: bold;">3.3.Licensor’s Warranties:</strong> <br>
            <strong style="color: black; font-weight: bold;">3.3.1.</strong>The Licensor warrants to the Licensee and User that it has sufficient rights and authority to grant to Licensee and User the rights as set out in these Terms.<br>
            <strong style="color: black; font-weight: bold;">3.3.2.</strong>The foregoing constitutes the Licensor’s only warranty to the Licensee and User. The Licensor does not warrant that the operation of the Services will be uninterrupted or error free or that the contents of the Services do not infringe any intellectual property rights.   To the extent permitted by law, the Licensor disclaims all warranties, whether express, implied or statutory, including but not limited to the implied warranties of merchantability and fitness for a particular purpose, availability, error-free or uninterrupted operation, and any warranties arising from a course of dealing, course of performance, or usage of trade to the extent not specifically prohibited under applicable law. The Services , their components, documentation and all other materials provided hereunder are provided “as is” and “as available” and the Licensor does not warrant that the Services are free of viruses, trojans or other malware.<br>
            <strong style="color: black; font-weight: bold;">4.	Shishughar App and Shishughar Website Downtime: </strong><br>
            The Licensor shall undertake reasonable efforts to minimize interruptions, errors, delays or other deficiencies in the Services . However, from time to time, there may be interruptions, errors, delays or other deficiencies that occur with respect to the Services due to various factors, including those that are beyond the control of the Licensor, which may require scheduled maintenance or lead to unscheduled downtime (collectively, “Downtime”). The Licensee/User acknowledges that the Services may temporarily be unavailable during such Downtime and that the Licensor shall not be held liable for any inconvenience or losses that may arise as a result of such Downtime. <br>
            <strong style="color: black; font-weight: bold;">5.	Data Protection and Privacy Policy</strong> <br>
            5.1.The Licensor collects, processes and uses personal data that the Licensee or any of its Users supply to the Licensor in the manner set out in the Privacy Policy annexed to these Terms and in compliance with applicable data protection laws. <br>
            5.2.The Licensor is a not-for-profit charitable organization and therefore, any personal data that is collected and processed by the Licensor is for non-commercial purposes. The personal data is used to create the User’s Account and provide access to the Services.<br> 
            5.3.Non-personal or anonymous data may be collected automatically to improve functionality and the User’s experience with the Services . The Licensee and its Users agree that the Licensor owns all rights in and is free to use any such non-personal or anonymous data in any way it deems fit for development, diagnostic, corrective or for any other non-commercial purposes.<br>
            5.4.The Licensor is committed to the privacy of the Users, Licensees and Beneficiaries and will not share any personal information with any third party, or otherwise associate a cookie, web beacon, or other mechanism with personally identifiable information, without explicit consent from the Licensee or its Users. <br>
            5.5.The Licensor shall use the User Information as well as the Beneficiary Information only in the manner set out in the Privacy Policy annexed hereto.<br> 
            <strong style="color: black; font-weight: bold;">6.Intellectual Property Rights:</strong> <br>
            6.1.All rights, title, interest and intellectual property rights in and to the Services , related documentation, user manuals and all components thereof or any modifications, customizations, new versions, upgrades, updates and enhancements thereto, either prior to the Effective Date, or during the Term shall always vest in the Licensor. Nothing herein shall convey title or any proprietary rights in or over the Services or any modifications, customizations, new versions, upgrades, updates and enhancements thereto to the Licensee or any of its Users.<br>
            6.2.The Licensor shall have the exclusive right to use, assign, delegate, license, or transfer any of its rights in respect of the Services.<br>
            6.3.The Licensee/User unreservedly acknowledge the Licensor’s ownership of the Services , and hereby undertakes not to do, permit or suffer anything to be done, which may infringe the Licensor’s intellectual property rights, or otherwise interfere with the Licensor’s exercise of the intellectual property rights, in any manner whatsoever.<br>
            <strong style="color: black; font-weight: bold;">7.	Term and Termination</strong><br>
            7.1.These Terms shall remain in force from the date on which the Licensee/User agrees to the same (“Effective Date”) until the Licensee/User (as the case may be) has access to the Services , unless otherwise terminated in accordance with these Terms (“Term”). <br>
            7.2.The Licensee/User acknowledges that grant of license of the Services by the Licensor under this Agreement is for a charitable purpose and not for making any profits, and that the Licensor may, in its sole discretion, terminate these Terms and cease to provide, to the Licensee/its Users, any services or access to the Services , or any portion thereof, without any notice.<br>
            7.3.Notwithstanding Clause 5.1 of these Terms, Licensor may terminate these Terms for any reason or no reason at all. Upon termination, for any reason, Licensee/User agrees to immediately discontinue all use of the Services .<br>
            7.4.Upon termination, for any reason, Clause 3 (Representations and Warranties), Clause 9 (Indemnification), Clause 6 (Term and Termination), Clause 8 (Confidentiality Obligations) and Clause 11 (Governing Law and Dispute Resolution) of the Terms shall continue in full force and effect.
            <br>
            <strong style="color: black; font-weight: bold;">8.Breach of Terms of Use</strong> <br>
            If the Licensee/User has reasonable grounds to believe that they have, violated these Terms, or that the Licensee’s/User’s use of the Services conflicts or interferes with  reputation of the Licensor, its interest or might subject the Licensor to unfavourable legal or regulatory action in any way, Licensor may indefinitely suspend or terminate access to the Services at any time, and report such action to relevant authorities. Licensor reserves the right to take recourse to all available remedies under applicable law in furtherance of the above.<br>
            <strong style="color: black; font-weight: bold;">9.Confidentiality Obligations</strong> <br>
            <strong style="color: black; font-weight: bold;">9.1.“Confidential Information”</strong> means confidential or proprietary information of the Licensor, in any form, that was disclosed or provided to the Licensee/User or became known to the Licensee/User through their relationship under these Terms or supplied in connection with these Terms either marked as being confidential, or by its nature should be reasonably understood to be confidential. Confidential Information includes, without limitation, the terms of this Agreement, materials relating to the Services , all financial, technical, business, operational, commercial, administrative, marketing, planning, development, staff management, information and data, and all other information, specification, analyses, data, designs, experience, inventions, trade secrets, product information, know-how, computer software, applications, systems and/or programmes, either directly or indirectly disclosed, communicated, corresponded or in any way, made available by the Licensor to the Licensee/User, regardless of the means of transmission and whether in tangible or electronic format. Confidential Information shall also include information discussed with the Licensee/User, either orally, visually, in writing (including graphic material), electronically or otherwise. Confidential information does not include any information that (i) is known to the Licensee/User, before receipt thereof; (ii) is disclosed to the Licensee/User by a Person who is under no obligation of confidentiality to the Licensor hereunder with respect to such information and who otherwise has a right to make such disclosure; (iii) is or becomes generally known in the public domain through no fault of the Licensee/User; or (iv) is independently developed by the Licensee/User without the aid of, access to or use of the Licensor’s Confidential Information.<br>

            9.2.During the Term, and following the expiry or the termination of this Agreement for whatever reason, the Licensee agrees to, and will cause its Users, agents, representatives, affiliates, subsidiaries, employees, officers and directors, as the case may be, to: <br>
            i.treat and hold as confidential the Confidential Information received from the Licensor from the Effective Date and exercise at least the same degree of care in doing so, that it extends to its own confidential information; <br>
            ii.use the Confidential information only for the purpose for which it was disclosed to it and limit access to such Confidential Information to those of its directors, partners, agents or employees, and bind each of its directors, partners, advisors, agents or employees, sub-contractors so involved to protect the Confidential Information and in the manner prescribed by the Licensor; <br>
            iii.immediately notify the Licensor, in writing, of any suspected or actual loss or unauthorized use, copying, or disclosure of the Confidential Information; and <br>
            iv.	upon demand, or upon expiry of, or termination of these Terms (for whatever reason), return all Confidential Information (including any copies thereof) in its possession or control to the Licensor, regardless of the form or medium of such Confidential Information, and shall ensure that all electronic, or otherwise non-returnable embodiments of the Confidential Information are promptly and permanently deleted.<br>
            v.Additionally, the Licensee agrees that any of its Users, agents, representatives, affiliates, subsidiaries, employees, officers or directors becomes legally compelled under applicable law (including a court order, or other legal, quasi-legal or regulatory agency’s request or similar process) to disclose any such Confidential Information, the Licensee shall immediately upon receipt of such an order or request, notify the Licensor of the same in writing, so that the Licensor may take the necessary steps to apply for a protective order. In the event that such protective order or other remedy is not obtained, or the Licensor waives compliance, the Licensee shall furnish only that portion of such Confidential Information which it is legally required to disclose and shall exercise best efforts to obtain assurances that confidential treatment will be accorded to information so disclosed by it to the competent authorities.
            <br>
            <strong style="color: black; font-weight: bold;">10.Indemnification</strong><br>
            10.1.The Licensee agrees to defend, indemnify, and hold harmless the Licensor, its officers, directors, managers and employees (“Licensor’s Indemnitees”) from any and all liabilities, costs, expenses incurred by the Licensor’s Indemnitees in connection with any claim, proceedings, action of whatever kind, formal or informal arising out of or in connection with:<br>
            i.the Licensee’s or any of its Users’ breach of the terms set forth in this Agreement; <br>
            ii.a claim of infringement of any copyright, patent, trade secret or trademark of any third party by the use of the Services (or any component thereof) by any of the Licensee’s Users, or any unauthorized use of the Services by the Licensee, or any of its Users, agents, employees, or any third parties engaged by it; <br>
            iii.any default, or failure on the part of the Licensee or its Users to conform to or comply with applicable laws;
            iv.the use by any of the Licensee’s Users of other than the latest version of the Services , if such infringement could have been avoided by the use of the latest version;<br>
            v.the use or combination of the Services , hardware or other materials not recommended by the Licensor, provided such infringement would not have arisen but for such use or combination; or <br>
            vi.use by the Licensee or any of its Users of the Services in a manner other than that for which it was designed or contemplated as evidenced by documentation / user manual provided by the Licensor.<br>
            10.2.The Licensee hereby acknowledges and agrees that in the event of any breach of these Terms by the Licensee, or any of its Users, the Licensor will suffer an irreparable injury, such that no remedy at law will afford it adequate protection against, or appropriate compensation for, such injury. Accordingly, the Licensee hereby agrees that the Licensor shall be entitled to specific performance of the Licensee’s or any of its User’s obligations under these Terms, as well as such further relief as may be granted by a court of competent jurisdiction. <br>
            10.3.The Licensee understands and agrees that, given the unique nature of the Services , any breach of these Terms by the Licensee or any of its Users will result in the Licensor suffering irreparable harm, for which monetary damages would provide inadequate compensation. Accordingly, the Licensee agrees that the Licensor will, in addition to any other remedies available to it at law or in equity, be entitled to seek immediate injunctive relief to enforce these Terms. The Licensee agrees that in such an event, it will contemporaneously pay all reasonable costs and fees incurred by the Licensor in connection with the prosecution and enforcement of same. <br>
            10.4.In no event shall the Licensor have any liability to the Licensee or any if its Users for any lost profits, loss of use, costs of procurement of substitute goods or services, or for any direct, compensatory, indirect, special, incidental, punitive, or consequential damages however caused and, whether in contract, tort or under any other theory of liability, whether or not the Licensee or its Users have been advised of the possibility of such damage.
            11.Limitation of Liability <br>
            11.1.Notwithstanding anything to the contrary contained in these Terms, the Parties shall not, under any circumstances whatsoever, be liable (whether by way of indemnity or otherwise) for any consequential, indirect, incidental, special, or punitive damages, whether foreseeable or unforeseeable (including claims for loss of goodwill, loss of profits, loss of business).<br>
            11.2.The Licensee/User acknowledges that grant of license of the Services by the Licensor under this agreement is for a charitable purpose and not for making any profits, and that the Licensor shall not be liable for any damages, of whatever kind, or to indemnify the Licensee or any of its Users, for any loss or claim against the Licensee/Users, arising from or in connection with, or relating to, the Services or these Terms. <br>
            <strong style="color: black; font-weight: bold;">12.Governing Law and Dispute Resolution</strong>  
            12.1.Any disputes arising from or with respect to these Terms shall be governed by the laws of India.<br>
            12.2.The Parties shall endeavour to amicably settle and resolve any dispute or difference arising out of or in relation to these Terms, failing which any Party may refer any disputes arising out of or in connection with these Terms for Arbitration as per the Arbitration and Conciliation Act, 1996. The seat of arbitration shall be Bangalore. The arbitration shall be conducted in English. The cost of arbitration, and specifically the fees and expenses of the arbitrator shall be shared equally by the Parties unless the award provides otherwise.<br>
            <strong style="color: black; font-weight: bold;">13.Force Majeure</strong> <br>
            Notwithstanding anything to the contrary herein contained, the Licensor shall have the right to forthwith terminate these Terms by notice to Licensee/User upon the occurrence of any event of force majeure, i.e. any event due to causes beyond the Licensee’s/User’s reasonable control, which could not be foreseen with reasonable diligence, and which substantially affects the performance of these Terms, but does not include any event that is attributable to the fault or negligence or carelessness of the Licensee, including but not limited to acts of God, fire, flood or other natural catastrophes; any law, order, regulation, direction, action of any civil or military authority, national emergencies, insurrections, riots, wars, (“Force Majeure Event”), where such a Force Majeure Event subsists for a continuous period exceeding 45 (forty five) days, with the result that the Licensee/User  are substantially unable to perform their obligations hereunder. Provided that none of the Parties shall be held liable for any delay/non-performance of their respective obligation during such period of Force Majeure Event for reasons solely attributable to the said event. <br>
            <strong style="color: black; font-weight: bold;">14.Amendments</strong>
            <br>
            The Licensor shall be entitled to modify these Terms at any time, at its sole discretion without any prior notice. The Licensee/User is responsible for regularly reviewing information posted on the Shishughar App or the Shishughar Website to obtain timely notice of such changes. The Licensee’s/User’s continued use of the Services following any such amendment indicates the Licensee’s/User’s acceptance of such amendment. <br>
            <strong style="color: black; font-weight: bold;">15.Communication</strong> <br>
            Notices, demands or other communication required or permitted to be given or made under these Terms to the Licensor shall be in writing and delivered personally or sent by registered post/ acknowledgment due, courier or electronic mail addressed to the Licensor at its address captured hereinbelow. <br>
            </p5>
            <h2>PRIVACY POLICY</h2>
            <br>
            Azim Premji Philanthropic Initiatives Pvt Ltd (‘APPI’, 'Philanthropic Initiatives’, 'we', 'us', or 'our',) is implementing a programme for supporting decentralized community-based day care centers/creches where caregivers may leave their children (“Programme”). These day care centers are also known as Shishughars (“Shishughar/s”). APPI has partnered with non-government organizations (“Partner NGOs”/ “Licensee/s”), who will be implementing the Shishughar Programme (“Programme”) and managing the day- to-day operations of the day care centers. In this regard, APPI has developed a mobile application called the ‘Shishughar App’ and a website called ‘Shishughar Website” (collectively, “Services”) to support the NGOs in implementing the Programme and review the implementation of the said Programme by the NGOs. This Privacy Policy describes how and why we might collect, store, use, and/or share ('Process') information when the Partner NGOs through any of its representatives (“User/s”) use the Services . 
            We hope you take some time to read through this Privacy Policy carefully, as it is important. If there are any terms in this Privacy Policy that you do not agree with, please discontinue use of our Services immediately.
            This Privacy Policy is applicable to the personal information collected through/uploaded on the Shishughar App or Shishughar Website.<br>
            <h3>Part A – Pertaining to User’s Personal Information</h3> <br>
            <strong style="color: black; font-weight: bold;">1.What information do we collect?</strong><br>
            We collect information including personal information from Users who will be using/accessing the Services on behalf of the Licensees. <br>

            1.1.The personal information we collect from Users who will be using and accessing the Services includes but is not limited to the – <br>
            a.	Name of the person <br>
            b.	Contact number <br>
            c.	Email address <br>
            d.	Geolocation <br>
            1.2.In order to maintain security and operation of the Services, for troubleshooting and for our internal analytics and reporting purposes, we may collect the following information if you choose to provide us with access and permission – <br>
            a.Geolocation Information. We may request access or permission to track location-based information from your mobile device, either continuously or while you are using our Services, to provide certain location-based services. If you wish to change our access or permissions, you may do so in your device's settings.
            <br>
            b.Mobile Device Access. We may request access or permission to certain features from your mobile device, including your mobile device's camera, microphone, storage, and other features. If you wish to change our access or permissions, you may do so in your device's settings.
            <br>
            c.Mobile Device Data. We automatically collect device information (such as your mobile device ID, model, and manufacturer), operating system, version information and system configuration information, device and application identification numbers, browser type and version, hardware model Internet service provider and/or mobile carrier, and Internet Protocol (IP) address (or proxy server). If you are using our Services, we may also collect information about the phone network associated with your mobile device, your mobile device’s operating system or platform, the type of mobile device you use, your mobile device’s unique device ID, and information about the features of our application(s) you accessed.<br>
            d.Push Notifications. We may request to send you push notifications regarding your Account or certain features of the Services. If you wish to opt out from receiving these types of communications, you may turn them off in your device's settings. <br>
            1.3.We automatically collect certain information when you visit, use, or navigate the Services . This information does not reveal your specific identity (like your name or contact information) but may include device and usage information, such as your IP address, browser and device characteristics, operating system, language preferences, referring URLs, device name, country, location, information about how and when you use our Services, and other technical information. This information is primarily needed to maintain the security and operation of our Services, and for our internal analytics and reporting purposes.<br>
            1.4.We may also collect information through cookies and similar technologies. The information we collect includes- <br>
            a.Log and Usage Data. Log and usage data is service-related, diagnostic, usage, and performance information our servers automatically collect when you access or use our Services and which we record in log files. Depending on how you interact with us, this log data may include your IP address, device information, browser type, and settings and information about your activity in the Services (such as the date/time stamps associated with your usage, pages and files viewed, searches, and other actions you take such as which features you use), device event information (such as system activity, error reports (sometimes called 'crash dumps'), and hardware settings).<br>
            b.Device Data. We collect device data such as information about your computer, phone, tablet, or other device you use to access the Services. Depending on the device used, this device data may include information such as your IP address (or proxy server), device and application identification numbers, location, browser type, hardware model, Internet service provider and/or mobile carrier, operating system, and system configuration information.<br>
            c.Location Data. We collect location data such as information about your device's location, which can be either precise or imprecise. How much information we collect depends on the type and settings of the device you use to access the Services. For example, we may use GPS and other technologies to collect geolocation data that tells us your current location (based on your IP address). You can opt out of allowing us to collect this information either by refusing access to the information or by disabling your Location setting on your device. However, if you choose to opt out, you may not be able to use certain aspects of the Services.<br>
            <strong style="color: black; font-weight: bold;">2.How do we process your information?</strong><br>
            We process your information including your personal information to provide, improve, and administer our Services, to communicate with you, for security and fraud prevention, and to comply with the law. We may also process your information for other purposes with your consent. <br>
            <strong style="color: black; font-weight: bold;">3.When and with whom do we share your personal information?</strong><br>
            We do not share your personal information that we collect with any third party, without prior consent. <br>
            <strong style="color: black; font-weight: bold;">4.Do we use cookies and other tracking technologies?</strong> <br>
            We may use cookies and similar tracking technologies (like web beacons and pixels) to access or store information. Specific information about how we use such technologies and how you can refuse certain cookies is set out in our Cookie Notice.<br>
            <strong style="color: black; font-weight: bold;">5.How long do we keep your information?</strong><br>
            We only keep the personal information we collect for as long as it is necessary for the purposes set out in this Privacy Policy, unless a longer retention period is required or permitted by law (such as for accounting or other legal requirements). <br>
            <strong style="color: black; font-weight: bold;">6.What are your privacy rights?</strong> <br>
            Users, whose personal information we collect have the right to correct/modify the personal information provided to us as well as withdraw their consent for the processing of such personal information. <br>
            However, please note that this will not affect the lawfulness of the processing before its withdrawal nor, when applicable law allows, will it affect the processing of personal information conducted in reliance on lawful processing grounds other than consent.
            <br>
            Cookies and similar technologies: Most Web browsers are set to accept cookies by default. If you prefer, you can usually choose to set your browser to remove cookies and to reject cookies. If you choose to remove cookies or reject cookies, this could affect certain features or services of our Services. To opt out of interest-based advertising by advertisers on our Services, visit http://www.aboutads.info/choices/.
            <br>
            If you have questions or comments about your privacy rights, you may email us at philanthropy.apps [@] azimpremjifoundation.org.
            <br>
            <strong style="color: black; font-weight: bold;">7.Controls for Do-Not-Track</strong> <br>
            Most web browsers and some mobile operating systems and mobile applications include a Do-Not-Track ('DNT') feature or setting you can activate to signal your privacy preference not to have data about your online browsing activities monitored and collected. At this stage no uniform technology standard for recognising and implementing DNT signals has been finalised. As such, we do not currently respond to DNT browser signals or any other mechanism that automatically communicates your choice not to be tracked online. If a standard for online tracking is adopted that we must follow in the future, we will inform you about that practice in a revised version of this Privacy Policy. <br>

            <h3>Part B – Pertaining to Beneficiaries of the Programme</h3><br>
            <p>
            <strong style="color: black; font-weight: bold;">1.Do we collect and process personal or sensitive personal information of the Beneficiaries of the Programme? </strong>
            <br>
            We do not collect any personal or sensitive personal information from Beneficiaries. However, we process the personal and sensitive personal information of the Beneficiaries that is collected by Licensees and uploaded on to the Shishughar App or Shishughar Website by its Users. <br>

            <strong style="color: black; font-weight: bold;">2.For what purposes do we process Beneficiaries’ Information uploaded on the Shishughar App/Shishughar Website?</strong> <br>
            We process the Beneficiaries’ personal and sensitive personal information uploaded on the Shishughar App/Shishughar Website by the Licensees/their Users to support Licensees in implementing the Programme. We also process such information uploaded on the Shishughar App/Shishughar Website for reviewing and monitoring the progress of Licensees in implementing the Programme.<br>
            
            <strong style="color: black; font-weight: bold;">3.Who do we share Beneficiaries’ Information uploaded on the Shishughar App/Shishughar Website with? </strong> <br>
            We do not share personal information and sensitive personal information uploaded on the Shishughar App/Shishughar Website with any third party. <br>

            <strong style="color: black; font-weight: bold;">4.How long do we keep Beneficiaries’ Information?</strong> <br>

            We only keep personal information and sensitive personal information uploaded on the Shishughar App/Shisghughar Website for as long as it is necessary for the purposes set out in this Privacy Policy, unless a longer retention period is required or permitted by law (such as for accounting or other legal requirements). 
            <br>
            <strong style="color: black; font-weight: bold;">5.What are the obligations of Licensees with respect to Beneficiaries’ Information? </strong> <br>
            With regards to personal information and sensitive personal information collected from Beneficiaries and uploaded on to the Shishughar App/Shishughar Website, Licensees and their Users shall comply with applicable data protection laws. 
            Licensees’ responsibilities include but are not limited to: <>br
            (i)	providing sufficient notice to the Beneficiaries prior to collection of such personal information and sensitive personal information as per applicable data protection laws, <br>
            (ii)communicating to the Beneficiaries prior to collection, that such personal information and sensitive personal information will be uploaded to the Shishughar App/Shishughar Website and that the same may be used by us for evaluating the implementation of the Programme by the Licensee. <br>
            (iii)obtaining consent for collection of such personal and sensitive personal information from the Beneficiaries and for uploading the same on the Shishughar App/Shishughar Website, as per applicable data protection laws. <br>
            (iv)Correction or deletion of the personal and sensitive personal information collected by the Licensees and uploaded on the Shishughar App/Shishughar Website, upon the request of the Beneficiaries. <br>
            (v)	Informing us of withdrawal of consent of any Beneficiary for processing their personal or sensitive personal information collected by the Licensees/their Users and uploaded on the Shishughar App/Shishughar Website. However, please note that this will not affect the lawfulness of the processing before its withdrawal of consent nor, when applicable law allows, will it affect the processing of personal information/sensitive personal information conducted in reliance on lawful processing grounds other than consent. <br>

            <h3>Part C – Miscellaneous</h3><br>

            <strong style="color: black; font-weight: bold;">1.	How do we keep the information uploaded on the Shishughar App safe? </strong> <br>
            We have implemented appropriate and reasonable technical and organisational security measures designed to protect the security of any personal information we process. However, despite our safeguards and efforts to secure your information/Beneficiaries’ information uploaded by you on the Shishughar App/Shishughar Website, no electronic transmission over the Internet or information storage technology can be guaranteed to be 100% secure, so we cannot promise or guarantee that hackers, cybercriminals, or other unauthorised third parties will not be able to defeat our security and improperly collect, access, steal, or modify your information. Although we will do our best to protect the personal & sensitive information we collect/process, transmission of personal & sensitive information to and from our Shishughar App/Shishughar Website is at your own risk. The Licensees/their Users should only access the Services within a secure environment. <br>

            <br>
            <strong style="color: black; font-weight: bold;">2.Do we update this Privacy Policy?</strong> <br>
            We may update this Privacy Policy from time to time. The updated version will be indicated by an updated 'Revised' date and the updated version will be effective as soon as it is accessible. If we make material changes to this Privacy Policy, we may notify you either by prominently posting a notice of such changes or by directly sending you a notification. We encourage you to review this Privacy Policy frequently to be informed of how we are protecting your information.
            <br>
            <strong style="color: black; font-weight: bold;">3.How can you contact us about this Privacy Policy?</strong> <br>
            If you have questions or comments about this Privacy Policy, or if you wish to modify the personal information provided by you or withdraw your consent for the processing of the same, you may email us at philanthropy.apps [@]azimpremjifoundation.org or by post to:
            <p/>

            Address:
            Azim Premji Foundation Pvt Ltd
            #134 Doddakannelli, Next to Wipro Corporate Office, Sarjapur Road
            Bangalore, Karnataka 560035
            India

            Email: philanthropy.apps [@]azimpremjifoundation.org 
            The Licensee hereby agrees to and conveys its acceptance of these Terms of Use by clicking on the “I agree” button.
            The User hereby agrees to and conveys its acceptance to these Terms of Use by clicking on the “I agree” button. 

            </p5>

           </div>

        <div class="footer">
            <p>For any queries, contact us at <a href="mailto:philanthropy.apps [@]azimpremjifoundation.org">philanthropy.apps [@] azimpremjifoundation.org</a></p>
            <p>&copy; 2023 Azim Premji Foundation Pvt Ltd. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    return Response(html_content, content_type="text/html; charset=utf-8")